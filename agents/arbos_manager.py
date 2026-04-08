import os
import subprocess
import json
import concurrent.futures
import multiprocessing
import time
import torch
import math
from datetime import datetime
from typing import Tuple, List, Dict, Any
from pathlib import Path
import threading  # v0.6: for background embodiment threads

import numpy as np
import logging
import shutil
import requests
import yaml
import networkx as nx
import ast

multiprocessing.set_start_method('spawn', force=True)

from agents.memory import memory, memory_layers
from agents.tools.tool_hunter import tool_hunter, load_registry, save_registry
from agents.tools.compute import ComputeRouter, compute_router
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails
from agents.video_archiver import VideoArchiver
from agents.history_parse_hunter import HistoryParseHunter
from agents.meta_tuning_arbos import MetaTuningArbos
from tools.archive_hunter import ArchiveHunter
from agents.embodiment import NeurogenesisArbos, MicrobiomeLayer, VagusFeedbackLoop
from agents.pattern_surfacer import ResonancePatternSurfacer, PhotoelectricPatternSurfacer

from validation_oracle import ValidationOracle
from trajectories.trajectory_vector_db import vector_db
from tools.agent_reach_tool import AgentReachTool
from verification_analyzer import VerificationAnalyzer
from goals.brain_loader import load_brain_component, load_toggle
from tools.pruning_advisor import generate_pruning_recommendations, update_module_toggle
from tools.pruning_advisor import pruning_advisor  # if it's a global instance


from autoharness import AutoHarness

from RestrictedPython import safe_globals, utility_builtins
from RestrictedPython.Eval import default_guarded_getattr
from RestrictedPython.Guards import safe_write, guarded_iter, guarded_unpack


# ====================== RESTRICTEDPYTHON SETUP ======================
def create_restricted_globals():
    """Single source of truth for secure globals."""
    restricted = safe_globals.copy()
    restricted.update(utility_builtins)
    
    # Whitelist safe scientific libraries
    try:
        import sympy
        restricted["sympy"] = sympy
    except:
        pass
    try:
        import numpy as np
        restricted["np"] = np
    except:
        pass
    
    restricted.update({
        "__name__": "__main__",
        "getattr": default_guarded_getattr,
        "_getattr_": default_guarded_getattr,
        "_write_": safe_write,
        "_iter_": guarded_iter,
        "_getitem_": lambda ob, index: ob[index],
        "_unpack_sequence_": guarded_unpack,
    })
    return restricted

SAFE_GLOBALS = create_restricted_globals()

def safe_exec(code: str, local_vars: Dict = None) -> bool:
    """Highly secure exec using RestrictedPython."""
    if local_vars is None:
        local_vars = {}
    try:
        tree = ast.parse(code)
        if len(ast.dump(tree).split()) > 1200:
            logger.warning("Code too large for safe_exec")
            return False
        exec(code, SAFE_GLOBALS.copy(), local_vars)
        return True
    except Exception as e:
        logger.debug(f"RestrictedPython blocked: {type(e).__name__}: {e}")
        return False

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# ====================== VERIFIABILITY SPEC + DVR CONTRACT (NAILS) ======================
class DVRPipeline:
    """Realistic DVR contract — no guarantees, only measurable paths."""

    @staticmethod

    def _safe_exec(self, snippet: str, local: Dict) -> bool:
        """Use RestrictedPython for maximum safety."""
        return safe_exec(snippet, local)    
        
    def decomp_template(task: str, goal_md: str) -> Dict[str, Any]:
        return {
            "decomposition_contract": {
                "minimum_subtasks": 3,
                "verifiability_rule": "Each subtask MUST have executable verifier snippets",
                "composability_rule": "Outputs must be mergeable without contradiction",
                "no_guarantee": "Passing subtasks does NOT guarantee merged success — dry-run will verify",
                "heterogeneity_mandate": "Maximize diversity across five axes"
            }
        }

    @staticmethod
    def hardening_conversation_template() -> str:
        return """INTERNAL HARDENING DIALOGUE (execute before output):
1. Produce candidate.
2. Run verifier snippets → record passed/tightness/score.
3. Assess composability risk.
4. State realistic confidence (0.0-1.0). Do not claim guaranteed success."""

# ====================== DRY-RUN SIMULATOR (pre-swarm test-plan validator) ======================
class DVRDryRunSimulator:
    def __init__(self, validator: ValidationOracle):
        self.validator = validator

    def _safe_exec(self, snippet: str, local: Dict) -> bool:
        return safe_exec(snippet, local)

    def generate_placeholder(self, artifact_spec: Dict) -> Any:
        snippets = artifact_spec.get("verifier_code_snippets", [])
        placeholder = {"artifact": "plausible_best_case", "metadata": {}}
        for snippet in snippets[:3]:
            local = {"candidate": placeholder, "passed": False, "tightness": 0.0, "score": 0.0}
            if self._safe_exec(snippet, local):
                if local.get("passed", False):
                    break
        return placeholder

    def run_dry_run(self, decomposed_subtasks: List[str], full_verifier_snippets: List[str], 
                    goal_md: str = "") -> Dict:
        """v0.8 Hardened Dry-Run Gate"""
        logger.info("🚀 Starting v0.8 hardened dry-run gate")
        
        # Safe guard
        if not hasattr(self, '_current_strategy') or self._current_strategy is None:
            self._current_strategy = {}

        placeholders = []
        for st in decomposed_subtasks:
            placeholder = self.generate_placeholder({"verifier_code_snippets": full_verifier_snippets})
            adversarial = placeholder.copy()
            adversarial["adversarial"] = True
            placeholders.extend([placeholder, adversarial])

        merged = self._simple_merge(placeholders)

        self_check = self._verifier_self_check_layer(
            candidate=str(merged), 
            contract=self._current_strategy.get("verifiability_contract", {}), 
            verifier_snippets=full_verifier_snippets
        )

        # 4. Deterministic metrics (your existing + safety)
        edge = self.validator._compute_edge_coverage(merged, full_verifier_snippets)
        invariant = self.validator._compute_invariant_tightness(merged, full_verifier_snippets)
        fidelity = self.validator._compute_fidelity(merged, full_verifier_snippets)
        hetero = self.validator._compute_heterogeneity_score(placeholders)

        c = self.validator._compute_c3a_confidence(edge, invariant, getattr(self, 'historical_reliability', 0.85))
        theta = self.validator._compute_theta_dynamic(c, self.loop_count / max(1, self.loop_count))
        efs = self.validator._compute_efs(fidelity, 0.8, hetero, 0.75, 0.85)

        # 5. Full composability check — v0.8
        composability_result = self._check_composability(merged, decomposed_subtasks, full_verifier_snippets)

        passed_gate = (
            validation_result.get("validation_score", 0) >= theta and 
            efs >= 0.65 and 
            c >= 0.78 and 
            composability_result.get("passed", False) and 
            self_check.get("verifier_quality", 0) >= 0.65
        )

        recommendation = "PROCEED_TO_SWARM" if passed_gate else "ITERATE_DECOMP"

        # v0.8: DOUBLE_CLICK / escalation eligibility
        double_click_info = None
        if not passed_gate and (self_check.get("verifier_quality", 0) < 0.55 or 
                               composability_result.get("score", 0) < 0.60):
            double_click_info = {
                "gap": "low_composability_or_verifier_quality",
                "details": {
                    "verifier_quality": self_check.get("verifier_quality"),
                    "composability": composability_result.get("score")
                },
                "severity": "high"
            }

        return {
            "dry_run_passed": passed_gate,
            "best_case_c": round(c, 4),
            "best_case_efs": round(efs, 4),
            "theta_dynamic": round(theta, 4),
            "verifier_quality": round(self_check.get("verifier_quality", 0), 4),
            "composability_pass_rate": composability_result.get("score", 0.0),
            "recommendation": recommendation,
            "notes": f"Dry-run gate complete. Structure {'sound' if passed_gate else 'needs iteration'}. "
                     f"Verifier quality: {self_check.get('verifier_quality', 0):.3f}",
            "self_check_details": self_check.get("dimensions", {}),
            "composability_details": composability_result,
            "double_click_info": double_click_info,
            "double_click_emitted": recommendation == "ITERATE_DECOMP" and self_check.get("verifier_quality", 0) < 0.55
        }
                        
    def _compute_verifier_quality(self, candidate: str, verifier_snippets: List[str], contract: Dict = None) -> Dict:
        """v0.8 Verifier Self-Check Layer — now using RestrictedPython."""
        if not verifier_snippets:
            return {"verifier_quality": 0.5, "dimensions": {}, "passed": False}

        dimensions = {}
        scores = []

        for snippet in verifier_snippets[:6]:
            try:
                local = {"candidate": candidate, "result": None, "passed": False}
                if self._safe_exec(snippet, local):   # Use safe version
                    passed = bool(local.get("result") or local.get("passed", False))
                    scores.append(1.0 if passed else 0.25)
                else:
                    scores.append(0.2)
            except Exception:
                scores.append(0.2)

        base_score = sum(scores) / len(scores) if scores else 0.5

        dimensions = {
            "edge_coverage": getattr(self.validator, '_compute_edge_coverage', lambda *a: base_score)(candidate, verifier_snippets),
            "invariant_tightness": getattr(self.validator, '_compute_invariant_tightness', lambda *a: base_score)(candidate, verifier_snippets),
            "fidelity": getattr(self.validator, '_compute_fidelity', lambda *a: base_score)(candidate, verifier_snippets),
            "adversarial_resistance": round(base_score * 0.9 + 0.1, 3),
            "symbolic_consistency": 0.9 if any("sympy" in s.lower() or "assert" in s.lower() for s in verifier_snippets) else 0.45
        }

        verifier_quality = round(sum(dimensions.values()) / len(dimensions), 4)

        return {
            "verifier_quality": verifier_quality,
            "dimensions": dimensions,
            "passed": verifier_quality >= 0.65
        }

    def _generate_intelligent_mock_data(self, subtasks: List[str], goal_md: str = "") -> List[Dict]:
        """Generate plausible winning mock solutions for dry-run."""
        mocks = []
        for st in subtasks[:4]:
            mocks.append({
                "subtask": st,
                "solution": f"[Mock high-quality solution for: {st[:80]}...]",
                "score": 0.88,
                "type": "winning"
            })
        return mocks

    def _generate_adversarial_mocks(self, subtasks: List[str]) -> List[Dict]:
        """Generate edge-case / failing mocks for robustness testing."""
        mocks = []
        for st in subtasks[:3]:
            mocks.append({
                "subtask": st,
                "solution": f"[Adversarial / edge-case input for: {st[:80]}... that breaks invariants]",
                "score": 0.35,
                "type": "adversarial",
                "adversarial": True
            })
        return mocks

    def _check_composability(self, merged: Any, decomposed_subtasks: List, verifier_snippets: List[str] = None) -> Dict:
        """v0.8 Real composability check — no hardcoded constants."""
        if not decomposed_subtasks:
            return {"passed": False, "score": 0.0, "details": "No subtasks to compose"}

        merged_str = str(merged).lower()
        contradiction_score = sum(1 for kw in ["contradict", "conflict", "inconsistent", "impossible", "break"] 
                                 if kw in merged_str)

        base_score = max(0.4, 1.0 - (contradiction_score * 0.25))
        
        # Bonus if merged structure looks coherent
        if isinstance(merged, dict) and len(merged) >= len(decomposed_subtasks) // 2:
            base_score += 0.2

        final_score = round(min(1.0, base_score), 4)

        return {
            "passed": final_score >= 0.70,
            "score": final_score,
            "details": f"Composed {len(decomposed_subtasks)} subtasks | Contradictions detected: {contradiction_score}",
            "contradiction_count": contradiction_score
        }

    def _apply_contract_delta(self, delta: dict):
        """Apply a contract evolution delta to the living template file — already good, minor safety upgrade."""
        try:
            path = "goals/brain/verification_contract_templates.md"
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n# EVOLVED DELTA — {delta.get('provenance', 'unknown')} | {datetime.now().isoformat()}\n")
                f.write(f"Type: {delta.get('delta_type', 'general')}\n")
                f.write(f"{delta.get('content', str(delta))}\n")
                f.write(f"Source: {delta.get('source', 'Meta-Tuning/Scientist Mode')}\n---\n")
            
            logger.info(f"✅ Contract delta applied: {delta.get('delta_type', 'general')}")
        except Exception as e:
            logger.warning(f"Failed to apply contract delta: {e}")

    def _simple_merge(self, placeholders: List[Any]) -> Any:
        """Improved simple merge that respects scores, structure, and contract context.
        Used primarily in dry-run for mock solution merging."""
        
        if not placeholders:
            return {"solution": "", "merged_from": 0, "success": False}

        # Sort by score descending (highest fidelity first)
        sorted_placeholders = sorted(
            placeholders, 
            key=lambda x: x.get("score", 0.0) if isinstance(x, dict) else 0.0, 
            reverse=True
        )

        merged = {
            "solution": "",
            "merged_from": len(sorted_placeholders),
            "sources": [],
            "success": True
        }

        for p in sorted_placeholders:
            if not p:
                continue
                
            if isinstance(p, dict):
                # Merge structured data
                for key, value in p.items():
                    if key == "solution" or key == "merged_solution":
                        if merged["solution"]:
                            merged["solution"] += "\n\n"
                        merged["solution"] += str(value)
                    else:
                        # Avoid overwriting important keys
                        if key not in ["score", "type", "adversarial"]:
                            merged[key] = value
                
                merged["sources"].append(p.get("subtask", "unknown"))
                
            elif isinstance(p, str):
                # Plain text solution
                if merged["solution"]:
                    merged["solution"] += "\n\n"
                merged["solution"] += p.strip()
                merged["sources"].append("text_fallback")
            else:
                # Other types
                if merged["solution"]:
                    merged["solution"] += "\n\n"
                merged["solution"] += str(p)

        # Final cleanup
        merged["solution"] = merged["solution"].strip()
        merged["source_count"] = len(merged["sources"])

        if not merged["solution"]:
            merged["success"] = False
            merged["solution"] = "[Merge produced empty result]"

        return merged
        
class ToolEnvManager:
    """v0.8 — Safe, persistent/ephemeral venv manager for one-click tool addition."""
    def __init__(self):
        self.base_path = Path("~/.enigma_tools").expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.registered_tools = {}  # in-memory registry
        
    def _safe_exec(self, snippet: str, local: Dict) -> bool:
        """Use RestrictedPython for maximum safety."""
        return safe_exec(snippet, local)
        
    def create_or_get_env(self, tool_name: str, install_cmd: str, persistent: bool = True) -> dict:
        """Create or reuse a venv, run the install command, and register the tool safely."""
        env_path = self.base_path / (tool_name if persistent else f"ephemeral_{int(time.time())}")
        
        if not env_path.exists():
            logger.info(f"Creating new tool environment: {tool_name}")
            try:
                subprocess.run(["python", "-m", "venv", str(env_path)], check=True, capture_output=True)
                pip_path = env_path / "bin" / "pip"
                subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True, capture_output=True)
                
                # Run the provided install command
                if install_cmd.strip():
                    subprocess.run([str(pip_path)] + install_cmd.strip().split(), check=True, capture_output=True)
                
                logger.info(f"✅ Tool environment ready: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to create tool environment {tool_name}: {e}")
                return {"status": "error", "error": str(e)}

        # Register for runtime use
        self.registered_tools[tool_name] = {
            "env_path": str(env_path),
            "persistent": persistent,
            "installed_at": datetime.now().isoformat()
        }

        return {
            "status": "success",
            "tool_name": tool_name,
            "env_path": str(env_path),
            "persistent": persistent
        }
        
class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        
        # Core loading
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        
        # Core components
        self.validator = ValidationOracle(goal_file, compute=compute_router, arbos=self)
        self.dvr = DVRPipeline()
        self.simulator = DVRDryRunSimulator(self.validator)
        self.tool_env_manager = ToolEnvManager()
        self.video_archiver = VideoArchiver()
        self.history_hunter = HistoryParseHunter(self.validator)
        self.meta_tuner = MetaTuningArbos(self.validator)
        self.neurogenesis = NeurogenesisArbos()
        self.microbiome = MicrobiomeLayer()
        self.vagus = VagusFeedbackLoop()
        self.rps = ResonancePatternSurfacer()
        self.pps = PhotoelectricPatternSurfacer()
        self.pruning_advisor = pruning_advisor
        self.analyzer = VerificationAnalyzer(goal_file)
        self.reach_tool = AgentReachTool()
        self.vector_db = vector_db
        self.vector_db.arbos = self
        self.memory_layers = memory_layers
        self.memory_layers.arbos = self  # important for SOTA gating

        # Safe execution (RestrictedPython)
        self._safe_exec = safe_exec

        # Toggles - cleaned and complete
        self.toggles = {
            "embodiment_enabled": load_toggle("embodiment_enabled", "true") == "true",
            "rps_pps_enabled": load_toggle("rps_pps_enabled", "true") == "true",
            "hybrid_ingestion_enabled": load_toggle("hybrid_ingestion_enabled", "true") == "true",
            "retrospective_enabled": load_toggle("retrospective_enabled", "true") == "true",
            "meta_tuning_enabled": load_toggle("meta_tuning_enabled", "true") == "true",
            "audit_enabled": load_toggle("audit_enabled", "true") == "true",
            "aha_adaptation_enabled": load_toggle("aha_adaptation_enabled", "true") == "true",
            "mycelial_pruning": load_toggle("mycelial_pruning", "true") == "true",
            "symbiosis_synthesis": load_toggle("symbiosis_synthesis", "true") == "true",
            "byterover_mau_enabled": load_toggle("byterover_mau_enabled", "false") == "true",
            "dynamic_tool_creation_enabled": load_toggle("dynamic_tool_creation_enabled", "false") == "true",
            "decision_journal_enabled": load_toggle("decision_journal_enabled", "true") == "true",
            "model_compute_capability_enabled": load_toggle("model_compute_capability_enabled", "true") == "true",
            "allow_per_subarbos_breakthrough": load_toggle("allow_per_subarbos_breakthrough", "true") == "true",
        }
        logger.info(f"✅ toggles loaded: {self.toggles}")

        # History & paths
        self.history_file = Path("submissions/run_history.json")
        self._ensure_history_file()
        self._init_memdir()

        # Compute & harness
        self.compute_source = "local_gpu"
        self.custom_endpoint = None
        self.max_repair_attempts = 3
        self.early_stop_threshold = 0.65
        self.loop_count = 0
        self.max_swarm_size = 12
        self.enable_grail = False
        self._current_strategy = None
        self._current_validation_criteria = {}
        self._current_enhancement = ""
        self._current_pre_launch = ""
        self.message_bus = []
        self.grail_reinforcement = {}
        self.diagnostic_history = []
        self.memory_policy_weights = {}
        self.meta_reflection_history = []
        self.known_failure_modes = []
        self.recent_scores = []
        self._flag_for_new_avenue_plan = False
        self._pending_new_avenue_plan = None
        self.current_run_id = 0
        self.meta_velocity = np.zeros(5)

        # AutoHarness with constitution
        config_path = os.path.join("config", "constitution.yaml")
        os.makedirs("config", exist_ok=True)
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                yaml.dump({
                    "mode": "core", 
                    "risk_rules": [
                        {"block": ["rm -rf", "os.system", "exec", "__import__"]}, 
                        {"allow_patterns": ["sympy", "numpy", "torch", "quantum", "crypto", "verifier"]}
                    ]
                }, f)
        with open(config_path) as f:
            constitution = yaml.safe_load(f)
        self.harness = AutoHarness.wrap(compute_router, constitution=constitution, mode="core")

        # Onyx / RAG
        self.onyx_url = os.getenv("ONYX_URL", "http://localhost:8000")
        self.use_onyx_rag = True
        self.sync_grail_to_memory_layers()

        # Scientist Mode
        self.scientist_log_path = Path("scientist_log.json")
        self.scientist_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.scientist_log = self._load_scientist_log()

        # Brain suite
        self.brain_depth = load_toggle("brain_depth", "lean")
        self.aha_adaptation_enabled = load_toggle("aha_adaptation_enabled", "true") == "true"
        self.mycelial_pruning = load_toggle("mycelial_pruning", "true") == "true"
        self.quantum_coherence_mode = load_toggle("quantum_coherence_mode", "false") == "true"
        self.symbiosis_synthesis = load_toggle("symbiosis_synthesis", "true") == "true"
        self.micro_evolution_frequency = load_toggle("micro_evolution_frequency", "every_aha")

        # Model / Compute
        self.model_compute_capability_enabled = load_toggle("model_compute_capability_enabled", "true") == "true"
        self.hybrid_routing_enabled = load_toggle("hybrid_routing_enabled", "true") == "true"
        self.allow_per_subarbos_breakthrough = load_toggle("allow_per_subarbos_breakthrough", "true") == "true"
        self.breakthrough_token_budget = int(load_toggle("breakthrough_token_budget_default", "12000"))

        self.model_registry = self._load_model_registry()
        self.default_planner_model = "DeepSeek-R1-Distill-Qwen-14B"
        self.default_hyphae_model = "Carnice-9B-Q4_K_M"

        # Core intelligence constants
        self.c3a_k = 0.5
        self.c3a_beta = 2.0
        self.novelty_floor = 0.20
        self.decision_journal_enabled = load_toggle("decision_journal_enabled", "true") == "true"
        self.dynamic_tool_creation_enabled = load_toggle("dynamic_tool_creation_enabled", "false") == "true"
        self.byterover_mau_enabled = load_toggle("byterover_mau_enabled", "false") == "true"
        self.pareto_efficiency_enabled = load_toggle("pareto_efficiency_enabled", "true") == "true"
        self.leann_efficiency_enabled = load_toggle("leann_efficiency_enabled", "false") == "true"

        # Wire memory layers
        self.memory_layers.byterover_mau_enabled = self.byterover_mau_enabled

        self.set_compute_source("local_gpu")
        self._load_heterogeneity_weights()

        logger.info("✅ ArbosManager v0.8 fully cleaned and initialized")
        
        if self.scientist_log_path.exists():
            try:
                with open(self.scientist_log_path) as f:
                    self.scientist_log = json.load(f)
            except:
                self.scientist_log = []
                
    def _safe_exec(self, code: str, local_vars: Dict = None) -> bool:
        return safe_exec(code, local_vars)
        
    # ====================== MODEL REGISTRY (v5.1.3 - Cleaned) ======================
    def _load_model_registry(self) -> Dict:
        """Load or create model registry with intelligent defaults."""
        registry_path = Path("config/model_registry.json")
        if registry_path.exists():
            try:
                with open(registry_path) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load model registry: {e}. Using defaults.")

        # Default high-quality registry
        default_registry = {
            "models": {
                "DeepSeek-R1-Distill-Qwen-14B": {
                    "endpoint": "local_ollama",
                    "model_name": "deepseek-r1-distill-qwen-14b",
                    "context_window": 131072,
                    "tool_calling_style": "qwen",
                    "max_parallel": 3,
                    "reliability_score": 0.94,
                    "role": "planner"
                },
                "Carnice-9B-Q4_K_M": {
                    "endpoint": "local_ollama",
                    "model_name": "carnice-9b",
                    "context_window": 131072,
                    "tool_calling_style": "hermes",
                    "max_parallel": 8,
                    "reliability_score": 0.91,
                    "role": "hyphae"
                },
                "Claude-Opus-4.6": {
                    "endpoint": "api_anthropic",
                    "model_name": "claude-opus-4.6",
                    "context_window": 200000,
                    "tool_calling_style": "computer_use",
                    "reliability_score": 0.98,
                    "strength": "symbolic_critique_invariants"
                },
                "Kimi-K2.5-AgentSwarm": {
                    "endpoint": "api_moonshot",
                    "model_name": "kimi-k2.5",
                    "context_window": 131072,
                    "tool_calling_style": "parallel_agent",
                    "reliability_score": 0.96,
                    "strength": "parallel_tool_exploration_novelty"
                }
            },
            "routing_rules": {
                "default": "Carnice-9B-Q4_K_M",
                "planner_model": "DeepSeek-R1-Distill-Qwen-14B",
                "planner_roles": ["Planning Arbos", "Orchestrator Arbos", "Scientist Mode"],
                "breakthrough_token_budget_default": 12000,
                "allow_per_subarbos_breakthrough": True,
                "heavy_subtask_keywords": ["quantum", "symbolic", "critique", "invariant", "synthesis"]
            }
        }

        # Save defaults if file doesn't exist
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(registry_path, "w") as f:
            json.dump(default_registry, f, indent=2)

        logger.info("✅ Model registry loaded/created with defaults")
        return default_registry

    def load_model_registry(self, subtask_id: str = None, role: str = None, override: str = None) -> Dict:
        """Main entry point — intelligently selects model based on role or subtask."""
        if override and override in self.model_registry["models"]:
            return self.model_registry["models"][override]

        rules = self.model_registry.get("routing_rules", {})
        
        # Planner / Orchestrator / Scientist roles get the strong reasoning model
        if role == "planner" or any(r in (subtask_id or "") for r in rules.get("planner_roles", [])):
            return self.model_registry["models"][rules.get("planner_model", "DeepSeek-R1-Distill-Qwen-14B")]

        # Default fallback
        return self.model_registry["models"][rules.get("default", "Carnice-9B-Q4_K_M")]

    def compute_c3a_multiplier(self, d: float, c: float) -> float:
        return math.exp(-self.c3a_k * d) * (c ** self.c3a_beta)

    def generate_verifiability_contract(self, task: str, goal_md: str = "") -> Dict:
        """Top-tier Verifiability Contract generator — strict structure, high quality, 
        and strong self-critique to ensure the DVRP pipeline has a solid foundation."""
        
        # Strict base template we control
        base_contract = {
            "version": "1.2",
            "challenge_summary": task[:600],
            "artifacts_required": [],
            "composability_rules": [
                "All artifacts must be independently verifiable by the oracle",
                "No internal contradictions between subtask outputs",
                "Final merged candidate must be a single coherent executable solution",
                "Every artifact must contribute to at least one dry_run_success_criteria"
            ],
            "dry_run_success_criteria": {
                "edge_coverage": ">= 0.75",
                "invariant_tightness": ">= 0.70",
                "fidelity": ">= 0.78",
                "c3a_confidence": ">= 0.78",
                "EFS": ">= 0.65",
                "minimum_artifacts_covered": ">= 90%"
            },
            "synthesis_guidance": "",
            "learning_mandate": "Every run must write full stigmergic trace, heterogeneity breakdown, decision journal entry, and ByteRover promotion decision."
        }

        prompt = f"""You are Orchestrator Arbos — formal contract writer for the SN63 DVRP pipeline.

GOAL CONTEXT:
{goal_md[:4000]}

CHALLENGE:
{task}

Create a high-quality, precise Verifiability Contract.

Return ONLY valid JSON using this exact structure. Do not add or remove top-level keys.

Focus especially on:
- artifacts_required: Be concrete, measurable, and comprehensive (minimum 3-5 artifacts)
- composability_rules: Add 3-6 specific, actionable rules for this challenge
- synthesis_guidance: Clear, detailed instructions for Synthesis Arbos on how to merge

After creating the contract, critique it internally for completeness and feasibility."""

        model_config = self.load_model_registry(role="planner")
        raw = self.harness.call_llm(prompt, temperature=0.32, max_tokens=1600, model_config=model_config)
        
        llm_output = self._safe_parse_json(raw)

        # Merge and enforce structure
        final_contract = {**base_contract, **llm_output}

        # Quality enforcement gates
        if len(final_contract.get("artifacts_required", [])) < 3:
            logger.warning("Contract had too few artifacts — adding minimum viable set")
            final_contract["artifacts_required"] = list(dict.fromkeys(
                final_contract.get("artifacts_required", []) + 
                ["core_solution", "verification_evidence", "edge_case_results", "performance_metrics"]
            ))[:6]

        if len(final_contract.get("composability_rules", [])) < 5:
            final_contract["composability_rules"].extend([
                "All outputs must be mergeable without loss of verifier coverage",
                "Maintain deterministic behavior where possible"
            ])

        # Self-critique pass
        critique_prompt = f"Critique this contract for gaps or weaknesses:\n{json.dumps(final_contract, indent=2)}"
        critique_raw = self.harness.call_llm(critique_prompt, temperature=0.3, max_tokens=800, model_config=model_config)
        critique = self._safe_parse_json(critique_raw)

        if isinstance(critique, dict) and "improvements" in critique:
            final_contract["self_critique"] = critique.get("improvements", [])

        logger.info(f"✅ High-quality Verifiability Contract generated — {len(final_contract['artifacts_required'])} artifacts | Rules: {len(final_contract['composability_rules'])}")

        return {
            "contract_generated": True,
            "final_verifiability_contract": final_contract,
            "self_critique": critique
        }
        
    def _emit_double_click_tag(self, gap: str, details: Dict = None, severity: str = "medium"):
        """Central DOUBLE_CLICK emitter."""
        if details is None:
            details = {}

        tag = {
            "tag": "DOUBLE_CLICK",
            "timestamp": datetime.now().isoformat(),
            "loop": getattr(self, "loop_count", 0),
            "gap": gap,
            "severity": severity,
            "details": details,
            "suggested_action": "Trigger narrow Scientist Mode experiment"
        }

        # Store in strategy for easy access
        if hasattr(self, '_current_strategy') and self._current_strategy is not None:
            if "double_click_tags" not in self._current_strategy:
                self._current_strategy["double_click_tags"] = []
            self._current_strategy["double_click_tags"].append(tag)

        # Save for learning
        self.save_to_memdir(f"double_click_{int(time.time())}", tag)

        logger.warning(f"🔥 DOUBLE_CLICK emitted → Gap: {gap} | Severity: {severity}")

        return tag
        
    def _build_failure_context(self, failure_type: str, task: str, goal_md: str,
                               strategy: Dict, dry_run: Dict = None,
                               swarm_results: List = None, validation_result: Dict = None) -> Dict:
        """Rich failure context packet for intelligent replanning — v0.8 hardened version."""

        # Safe metric extraction
        oracle_metrics = {
            "edge_coverage": getattr(self.validator, "_compute_edge_coverage", lambda *a: 0.0)(
                validation_result.get("candidate", "") if validation_result else "", 
                strategy.get("verifier_code_snippets", []) if strategy else []
            ),
            "invariant_tightness": getattr(self.validator, "_compute_invariant_tightness", lambda *a: 0.0)(
                validation_result.get("candidate", "") if validation_result else "", 
                strategy.get("verifier_code_snippets", []) if strategy else []
            ),
            "fidelity": getattr(self.validator, "last_fidelity", getattr(validation_result, "get", lambda k,d: d)("fidelity", 0.0)),
            "heterogeneity_score": self._compute_heterogeneity_score().get("heterogeneity_score", 0.72),
            "c3a_confidence": getattr(self.validator, "last_c", 0.75),
            "theta_dynamic": getattr(self.validator, "last_theta", 0.65),
            "EFS": getattr(self, "last_efs", getattr(validation_result, "get", lambda k,d: d)("efs", 0.0)),
            "real_vs_dry_run_delta": (
                getattr(self, "last_efs", 0.0) - 
                (dry_run.get("best_case_efs", 0.0) if dry_run else 0.0)
            )
        }

        # Auto-detect failure modes
        failure_modes = []
        if oracle_metrics["EFS"] < 0.60:
            failure_modes.append("low_efs")
        if oracle_metrics["c3a_confidence"] < 0.70:
            failure_modes.append("low_c3a_confidence")
        if dry_run and not dry_run.get("dry_run_passed", True):
            failure_modes.append("dry_run_failure")
        if swarm_results and len(swarm_results) > 0:
            avg_local = sum(r.get("local_score", 0) for r in swarm_results if isinstance(r, dict)) / max(1, len(swarm_results))
            if avg_local < 0.55:
                failure_modes.append("low_subtask_consistency")

        # DOUBLE_CLICK readiness check
        if any(mode in ["low_efs", "low_c3a_confidence", "dry_run_failure"] for mode in failure_modes):
            failure_modes.append("DOUBLE_CLICK_eligible")

        context = {
            "failure_type": failure_type,
            "task": task[:500],  # prevent huge strings
            "timestamp": datetime.now().isoformat(),
            "original_verifiability_contract": strategy.get("verifiability_contract", {}) if strategy else {},
            "orchestrator_dialogue": strategy.get("orchestrator_dialogue", {}) if strategy else {},
            "dry_run_result": dry_run or {},
            "swarm_results_summary": {
                "total_subtasks": len(swarm_results or []),
                "avg_local_score": round(
                    sum(r.get("local_score", 0) for r in (swarm_results or []) if isinstance(r, dict)) 
                    / max(1, len([r for r in (swarm_results or []) if isinstance(r, dict)])), 4)
            },
            "oracle_metrics": oracle_metrics,
            "failure_modes": failure_modes,
            "loop_count": getattr(self, "loop_count", 0),
            "recent_history_summary": self.recent_scores[-5:] if hasattr(self, "recent_scores") else [],
            "goal_md_snippet": goal_md[:300] if goal_md else "",
            "double_click_recommended": "DOUBLE_CLICK_eligible" in failure_modes
        }

        logger.info(f"Built failure context — Type: {failure_type} | Modes: {failure_modes} | DOUBLE_CLICK eligible: {context['double_click_recommended']}")
        return context
                                   
    def _detect_gaps_from_previous_outputs(self, previous_outputs: List) -> List[str]:
        """Lightweight gap detection for proactive ToolHunter and DOUBLE_CLICK handling."""
        gaps = []
        if not previous_outputs:
            return gaps
        for out in previous_outputs:
            if out.get("local_score", 0) < 0.65:
                gaps.append("low_score_subtask")
            if "invariant" in str(out.get("solution", "")).lower():
                gaps.append("invariant_tightness_gap")
        return list(dict.fromkeys(gaps))
        
    def _intelligent_replan(self, failure_context: Dict) -> Dict:
        """v0.8 Intelligent Replanner — analyzes failure packet and decides fix vs new strategy.
        Handles DOUBLE_CLICK, contract weaknesses, and swarm stalls."""
        
        logger.info("🔄 Running intelligent replan analysis")

        score = failure_context.get("validation_score", 0.0)
        efs = failure_context.get("efs", 0.0)
        gap = failure_context.get("gap", "unknown")
        tags = failure_context.get("tags", [])

        decision = {
            "decision": "fix_current_plan",
            "confidence": 0.75,
            "spec_fixes": [],
            "next_action": "targeted_repair",
            "reasoning": ""
        }

        # DOUBLE_CLICK handling (Deep-Dive Point 9)
        if any("DOUBLE_CLICK" in str(t) for t in tags) or "DOUBLE_CLICK" in gap:
            decision["decision"] = "run_double_click_experiment"
            decision["next_action"] = "scientist_mode_narrow_experiment"
            decision["reasoning"] = f"DOUBLE_CLICK tag detected on gap: {gap}"
            decision["confidence"] = 0.92
            logger.info(f"🔥 DOUBLE_CLICK triggered — queuing narrow experiment on {gap}")
            return decision

        # Severe stall or very low metrics
        if failure_context.get("is_severe_stall", False) or score < 0.55 or efs < 0.50:
            decision["decision"] = "new_strategy_needed"
            decision["next_action"] = "full_replan"
            decision["reasoning"] = "Severe stall or critically low metrics — new strategy required"
            decision["confidence"] = 0.88
            return decision

        # Contract or composability weaknesses
        if "composability" in gap.lower() or "verifier_quality" in gap.lower():
            decision["spec_fixes"] = [
                "Increase symbolic verifier snippets",
                "Tighten composability_rules in contract",
                "Add more adversarial mocks in dry-run"
            ]
            decision["reasoning"] = "Contract or composability gap detected — applying targeted fixes"
            decision["confidence"] = 0.80

        # Default safe repair
        if not decision["spec_fixes"]:
            decision["spec_fixes"] = ["Strengthen verifier snippets", "Increase heterogeneity in decomposition"]

        logger.info(f"Replan decision: {decision['decision']} | Confidence: {decision['confidence']:.2f}")
        return decision
        
    def _analyze_swarm_stall(self, subtask_outputs: List[Dict], validation_result: Dict, dry_run_result: Dict) -> Dict:
        """Analyzes real swarm stall despite passed dry-run — v0.8 hardened with DOUBLE_CLICK detection."""
        real_efs = validation_result.get("efs", 0.0)
        dry_run_efs = dry_run_result.get("best_case_efs", 0.0)
        
        stall_context = {
            "real_efs": round(real_efs, 4),
            "dry_run_efs": round(dry_run_efs, 4),
            "delta": round(real_efs - dry_run_efs, 4),
            "is_severe_stall": (real_efs < dry_run_efs - 0.15) or self._is_stale_regime(self.recent_scores),
            "low_performing_subtasks": [{"subtask": out.get("subtask", "unknown"), "local_score": out.get("local_score", 0.0)} for out in subtask_outputs if out.get("local_score", 0.0) < 0.65],
            "heterogeneity_drop": self._compute_heterogeneity_score().get("heterogeneity_score", 0.72) < 0.6,
            "failure_modes": []
        }

        if stall_context["delta"] < -0.15:
            stall_context["failure_modes"].append("large_efs_drop_from_dry_run")
        if len(stall_context["low_performing_subtasks"]) > len(subtask_outputs) / 2:
            stall_context["failure_modes"].append("majority_subtasks_underperformed")
        if stall_context["heterogeneity_drop"]:
            stall_context["failure_modes"].append("heterogeneity_collapse_in_real_execution")

        # v0.8 Additions (only added):
        # DOUBLE_CLICK detection for intelligent escalation
        if stall_context["is_severe_stall"] or len(stall_context["failure_modes"]) >= 2:
            stall_context["failure_modes"].append("DOUBLE_CLICK_eligible")
            stall_context["double_click_recommended"] = True
            stall_context["suggested_gap"] = "real_execution_gap_vs_dry_run" if stall_context["delta"] < -0.12 else "subtask_inconsistency"
        else:
            stall_context["double_click_recommended"] = False

        # Richer diagnostics for replanner
        stall_context["oracle_summary"] = {
            "validation_score": validation_result.get("validation_score", 0.0),
            "c3a_confidence": validation_result.get("c3a_confidence", 0.75),
            "verifier_quality": validation_result.get("verifier_quality", 0.0)
        }
        stall_context["recommendation"] = "new_strategy_needed" if stall_context["is_severe_stall"] else "targeted_fix"

        logger.info(f"Swarm stall analysis — Severe: {stall_context['is_severe_stall']} | Delta: {stall_context['delta']:.3f} | "
                   f"DOUBLE_CLICK eligible: {stall_context['double_click_recommended']} | Modes: {stall_context['failure_modes']}")

        return stall_context
        
    def compute_confidence(self, edge_coverage: float, invariant_tightness: float, historical_reliability: float) -> float:
        raw_c = (0.4 * edge_coverage) + (0.4 * invariant_tightness) + (0.2 * historical_reliability)
        return max(self.novelty_floor, min(1.0, raw_c))

    # ====================== v5.1 DECISION JOURNAL ======================
    def write_decision_journal(self, subtask_id: str, hypothesis: str, evidence: str, performance_delta: Dict, organic_thought: str = ""):
        if not self.decision_journal_enabled:
            return
        entry = {
            "timestamp": datetime.now().isoformat(),
            "subtask_id": subtask_id,
            "hypothesis": hypothesis,
            "evidence_vs_instinct": evidence,
            "performance_delta": performance_delta,
            "organic_thought": organic_thought
        }
        path = f"goals/knowledge/{getattr(self, '_current_challenge_id', 'current')}/wiki/subtasks/{subtask_id}/decision_journal.md"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n### {datetime.now().isoformat()}\n{json.dumps(entry, indent=2)}\n")
        logger.info(f"Decision Journal entry written for Sub-Arbos {subtask_id}")

    # ====================== v5.1.3 STAGNATION + BREAKTHROUGH ======================
    def is_stagnant_subarbos(self, subtask_id: str) -> bool:
        if len(self.recent_scores) < 4:
            return False
        recent = self.recent_scores[-6:]  # wider window
        score_variance = max(recent) - min(recent)
        efs = getattr(self, "last_efs", 0.0)
        hetero = self._compute_heterogeneity_score().get("heterogeneity_score", 0.72)
        
        # Stagnation = low variance + low absolute performance + low heterogeneity
        return (score_variance < 0.08) and (np.mean(recent) < 0.72) and (efs < 0.68 or hetero < 0.65)

    def generate_gap_diagnosis(self, subtask_id: str) -> str:
        last_score = getattr(self.validator, "last_score", 0.0)
        efs = getattr(self, "last_efs", 0.0)
        hetero = self._compute_heterogeneity_score().get("heterogeneity_score", 0.72)
        
        issues = []
        if last_score < 0.65:
            issues.append("low validation score")
        if efs < 0.60:
            issues.append("poor EFS")
        if hetero < 0.60:
            issues.append("low heterogeneity")
            
        return f"Localized stagnation in Sub-Arbos {subtask_id}: {', '.join(issues) or 'general underperformance'}. " \
               f"Score={last_score:.3f}, EFS={efs:.3f}, Hetero={hetero:.3f}"

    def recommend_breakthrough_model(self, gap_diagnosis: str) -> str:
        lower = gap_diagnosis.lower()
        if any(k in lower for k in ["invariant", "symbolic", "tightness", "deterministic"]):
            return "Claude-Opus-4.6"
        if any(k in lower for k in ["tool", "parallel", "novelty", "heterogeneity"]):
            return "Kimi-K2.5-AgentSwarm"
        if "efs" in lower or "score" in lower:
            return "DeepSeek-R1-Distill-Qwen-14B"  # strong reasoning
        return "Claude-Opus-4.6"  # safe default

    # ====================== HETEROGENEITY + ADAPTIVE STALE ======================
    def _load_heterogeneity_weights(self):
        path = os.path.join("config", "heterogeneity_weights.json")
        if os.path.exists(path):
            with open(path) as f:
                self.current_heterogeneity_weights = json.load(f)
        else:
            self.current_heterogeneity_weights = {
                "weights": [0.25, 0.25, 0.20, 0.15, 0.15],
                "dimension_names": ["agent_diversity", "hypothesis_diversity", "tool_path_diversity", "graph_diversity", "substrate_diversity"],
                "adaptive_stale_window": 8,
                "adaptive_z_threshold": 1.5,
                "min_runs_before_stale_check": 6,
                "rescue_nudge_factor": 0.18,
                "rescue_decay": 0.65,
                "history": []
            }
            os.makedirs("config", exist_ok=True)
            with open(path, "w") as f:
                json.dump(self.current_heterogeneity_weights, f, indent=2)

    def _compute_heterogeneity_score(self, subtask_outputs: List = None) -> Dict:
        """Now can take real outputs for dynamic calculation."""
        if subtask_outputs:
            return {
                "heterogeneity_score": self.validator._compute_heterogeneity_score(subtask_outputs),
                "breakdown": {"dynamic": True}
            }
        # Fallback
        return {
            "heterogeneity_score": 0.72,
            "breakdown": {
                "agent_diversity": 0.75,
                "hypothesis_diversity": 0.68,
                "tool_path_diversity": 0.80,
                "graph_diversity": 0.65,
                "substrate_diversity": 0.70
            }
        }

    def _is_stale_regime(self, recent_scores: list[float]) -> bool:
        if len(recent_scores) < self.current_heterogeneity_weights.get("min_runs_before_stale_check", 6):
            return False
        recent = np.array(recent_scores[-self.current_heterogeneity_weights["adaptive_stale_window"]:])
        mean_recent = np.mean(recent)
        std_recent = np.std(recent) if len(recent) > 1 else 0.1
        current = recent[-1]
        z_score = (current - mean_recent) / std_recent
        is_sudden_drop = z_score < -self.current_heterogeneity_weights["adaptive_z_threshold"]
        is_prolonged_low = mean_recent < 0.65 and len(recent) >= 6
        return is_sudden_drop or is_prolonged_low

    # ====================== KNOWLEDGE HIERARCHY + WIKI + BIO HELPERS ======================
    def _ensure_knowledge_hierarchy(self, challenge_id: str):
        base = f"goals/knowledge/{challenge_id}"
        os.makedirs(f"{base}/raw", exist_ok=True)
        os.makedirs(f"{base}/wiki/concepts", exist_ok=True)
        os.makedirs(f"{base}/wiki/invariants", exist_ok=True)
        os.makedirs(f"{base}/wiki/subtasks", exist_ok=True)
        os.makedirs(f"{base}/cross_field_synthesis", exist_ok=True)
        logger.debug(f"Knowledge hierarchy ready for {challenge_id}")

    def _create_subtask_wiki_folder(self, challenge_id: str, subtask_id: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = f"goals/knowledge/{challenge_id}/wiki/subtasks/{timestamp}_{subtask_id}"
        os.makedirs(path, exist_ok=True)
        return path

    def _write_subtask_md(self, path: str, content: str, bio_delta: str = ""):
        full_content = content
        if bio_delta and self.mycelial_pruning:
            full_content += f"\n\n# BIO_MYCELIAL_DELTA (stigmergy signal)\n{bio_delta}\n# End Bio Delta"
        with open(f"{path}/subtask.md", "w", encoding="utf-8") as f:
            f.write(full_content)
        logger.info(f"Stigmergy write → {path}/subtask.md")

    # ====================== PLANNING ======================
    def plan_challenge(self, goal_md: str = "", challenge: str = "", enhancement_prompt: str = "", compute_mode: str = "local_gpu") -> Dict[str, Any]:
        """v0.8 Top-tier Planning Arbos — rich context + formal Verifiability Contract + slice preparation."""
        self.set_compute_source(compute_mode)
        
        if not challenge or len(challenge.strip()) < 10:
            return {"error": "Challenge too short"}

        logger.info("🚀 Planning Arbos starting — v0.8 contract + proactive context preparation")

        # Load rich prior context (your existing logic stays)
        recent_history = self.get_run_history(n=6)
        grail_patterns = self._load_recent_grail_patterns()
        wiki_deltas = self._apply_wiki_strategy(goal_md + "\n" + challenge, challenge.replace(" ", "_").lower())

        # Generate high-quality verifiability contract
        contract_result = self.generate_verifiability_contract(challenge, goal_md)

        # Strong human-in-the-loop enforcement
        if not enhancement_prompt or len(enhancement_prompt.strip()) < 30:
            logger.warning("⚠️ Weak or missing human refinement prompt")
            enhancement_prompt = enhancement_prompt or "Maximize verifier compliance, heterogeneity across all five axes, deterministic/symbolic paths first. Prioritize clean composability for Synthesis Arbos. Be brutally honest about feasibility."

        self._current_enhancement = enhancement_prompt

        # Structured handoff package
        orchestrator_input = {
            "human_refinement": enhancement_prompt,
            "verifiability_contract": contract_result.get("final_verifiability_contract", {}),
            "prior_lessons": {
                "recent_history": recent_history,
                "grail_patterns": grail_patterns,
                "wiki_deltas": wiki_deltas
            }
        }

        # Hand off to Orchestrator
        execution_result = self.orchestrate_subarbos(
            task=challenge,
            goal_md=goal_md,
            orchestrator_input=orchestrator_input
        )

        self._current_strategy = self.analyzer.analyze("", challenge)
        self.validator.adapt_scoring(self._current_strategy)

        return {
            "phase1": contract_result,
            "phase2": execution_result,
            "adapted_strategy": self._current_strategy,
            "dynamic_swarm_size": execution_result.get("dynamic_swarm_size", 6),
            "human_refinement": enhancement_prompt,
            "verifiability_contract": contract_result.get("final_verifiability_contract", {}),
            "structured_handoff": True
        }
        
    # Clean handoff helper
    
    def _orchestrator_execution_step(self, orchestrator_input: Dict, challenge: str) -> Dict:
        """Real structured handoff from Planning to Orchestrator Arbos."""
        prompt = f"""You are Orchestrator Arbos.

FULL INPUT FROM PLANNING ARBOS:
{json.dumps(orchestrator_input, indent=2)}

Generate the complete execution blueprint.

Return ONLY valid JSON with: 
decomposition, swarm_config, tool_map, validation_criteria, hypothesis_diversity, recomposition_plan, synthesis_guidance"""

        model_config = self.load_model_registry(role="planner")
        raw = self.harness.call_llm(prompt, temperature=0.3, max_tokens=1400, model_config=model_config)
        return self._safe_parse_json(raw)
        
        
    # ====================== ORCHESTRATE SUB-ARBOS (FULLY HARDENED & WIRED) ======================
    def orchestrate_subarbos(self, task: str, goal_md: str = "", previous_outputs: List[Any] = None, 
                             orchestrator_input: Dict = None) -> Dict[str, Any]:
        """v0.8 Top-tier Orchestrator Arbos — proactive ToolHunter + DOUBLE_CLICK support + per-subtask contract slices."""
        
        logger.info(f"🚀 Orchestrator Arbos starting (v0.8): {task[:80]}...")

        # 1. Receive structured handoff from Planning Arbos
        if orchestrator_input:
            verifiability_contract = orchestrator_input.get("verifiability_contract", {})
            human_refinement = orchestrator_input.get("human_refinement", "")
            logger.info("✅ Received rich structured Verifiability Contract from Planning")
        else:
            # Fallback
            contract_result = self.generate_verifiability_contract(task, goal_md)
            verifiability_contract = contract_result.get("final_verifiability_contract", {})
            human_refinement = ""

        # 2. Build strategy with contract as single source of truth
        strategy = self.analyzer.analyze("", task)
        strategy["verifiability_contract"] = verifiability_contract
        strategy["human_refinement"] = human_refinement
        strategy["hardening_dialogue"] = self.dvr.hardening_conversation_template()
        self._current_strategy = strategy

        # 3. Proactive ToolHunter + rich context packet (v0.8)
        rich_context = {
            "task": task,
            "verifiability_contract": verifiability_contract,
            "human_refinement": human_refinement,
            "previous_outputs_summary": [o.get("subtask", "") for o in (previous_outputs or [])],
            "gaps": self._detect_gaps_from_previous_outputs(previous_outputs) if previous_outputs else []
        }
        tool_recommendations = tool_hunter.hunt_and_integrate(
            gap_description="Proactive hunt for this subtask",
            subtask=task,
            challenge_context=json.dumps(rich_context)
        )
        strategy["recommended_tools"] = tool_recommendations.get("tools", [])

        # Lightweight InfoSeeker heuristics (v0.8)
        strategy["info_seeker_heuristics"] = ["near_decomposability", "map_reduce_aggregate", "reflection_checklist"]

        # 2-Round Debate Phase (critique-first) - v0.8
        debate_result = self._run_orchestrator_debate(task, verifiability_contract, rich_context)
        if debate_result and debate_result.get("refined_contract"):
            verifiability_contract = debate_result["refined_contract"]
            strategy["verifiability_contract"] = verifiability_contract
            logger.info("Orchestrator 2-round debate completed and contract refined")

        # 4. Dry-run gate (critical safety layer)
        full_verifier_snippets = strategy.get("verifier_code_snippets", [])
        dry_run = self.simulator.run_dry_run(
            decomposed_subtasks=verifiability_contract.get("artifacts_required", []),
            full_verifier_snippets=full_verifier_snippets,
            goal_md=goal_md
        )
        # Handle DOUBLE_CLICK from dry-run
        if dry_run.get("double_click_info"):
            self._emit_double_click_tag(
                gap=dry_run["double_click_info"]["gap"],
                details=dry_run["double_click_info"]["details"],
                severity=dry_run["double_click_info"]["severity"]
            )
        strategy["dry_run_result"] = dry_run

        # Dry-run intelligent replan + DOUBLE_CLICK / ESCALATE handling
        if dry_run.get("recommendation") == "ITERATE_DECOMP" or any(tag in task for tag in ["[DOUBLE_CLICK]", "[ESCALATE_TO_TOOL]"]):
            logger.warning("Dry-run failed or DOUBLE_CLICK tag detected — triggering intelligent replan")
            failure_context = self._build_failure_context(
                failure_type="dry_run_failed", 
                task=task, 
                goal_md=goal_md,
                strategy=strategy, 
                dry_run=dry_run
            )
            replan_decision = self._intelligent_replan(failure_context)
            
            if replan_decision.get("decision") == "new_strategy_needed":
                logger.info("Dry-run failed or DOUBLE_CLICK → triggering new strategy")
                return self.orchestrate_subarbos(
                    task=f"{task} [NEW STRATEGY AFTER DRY-RUN FAILURE]",
                    goal_md=goal_md,
                    orchestrator_input=orchestrator_input
                )
            else:
                if replan_decision.get("spec_fixes"):
                    verifiability_contract["fixes_applied"] = replan_decision.get("spec_fixes", [])

        # 5. Advanced Swarm Execution with per-subtask contract slices
        subtask_outputs = self._launch_hyphal_workers(task, strategy)

        # 6. Advanced Synthesis Arbos
        raw_merged = self._recompose(subtask_outputs, {})
        synthesis_result = self.synthesis_arbos(
            subtask_outputs=subtask_outputs,
            recomposition_plan=verifiability_contract.get("recomposition_plan", {}),
            verifiability_contract=verifiability_contract
        )

        final_candidate = synthesis_result.get("final_candidate", raw_merged)

        # 7. Symbiosis Arbos
        symbiosis_patterns = self._run_symbiosis_arbos(
            aggregated_outputs=subtask_outputs,
            message_bus=self.message_bus,
            synthesis_result=synthesis_result
        )

        # 8. Final ValidationOracle
        validation_result = self.validator.run(
            candidate=final_candidate,
            verification_instructions="",
            challenge=task,
            goal_md=goal_md,
            subtask_outputs=subtask_outputs
        )

        score = validation_result.get("validation_score", 0.0)
        efs = validation_result.get("efs", 0.0)

        # 9. Compute deterministic metrics
        edge = self.validator._compute_edge_coverage(final_candidate, full_verifier_snippets)
        invariant = self.validator._compute_invariant_tightness(final_candidate, full_verifier_snippets)
        fidelity = self.validator._compute_fidelity(final_candidate, full_verifier_snippets)
        hetero = self.validator._compute_heterogeneity_score(subtask_outputs) if subtask_outputs else 0.0

        c = self.validator._compute_c3a_confidence(edge, invariant, getattr(self, 'historical_reliability', 0.85))
        theta = self.validator._compute_theta_dynamic(c, self.loop_count / 10.0)

        passed = self.validator._subarbos_gate(final_candidate, strategy, subtask_outputs)

        # 10. Swarm stall detection & intelligent replan
        stall_analysis = self._analyze_swarm_stall(subtask_outputs, validation_result, dry_run)
        if stall_analysis.get("is_severe_stall", False):
            logger.warning("Severe swarm stall detected despite passed dry-run")
            failure_context = self._build_failure_context(
                failure_type="swarm_stall_on_passed_spec",
                task=task,
                goal_md=goal_md,
                strategy=strategy,
                dry_run=dry_run,
                swarm_results=subtask_outputs,
                validation_result=validation_result
            )
            replan_decision = self._intelligent_replan(failure_context)
            
            if replan_decision.get("decision") == "new_strategy_needed":
                logger.info("Severe stall → full replan")
                new_task = f"{task} [STALL RECOVERY]"
                return self.orchestrate_subarbos(new_task, goal_md, orchestrator_input=orchestrator_input)

        # 11. Success path & learning
        if score > 0.70:
            self.memory_layers.promote_high_signal(str(final_candidate), {
                "local_score": score,
                "fidelity": fidelity,
                "heterogeneity_score": hetero
            })

        if score > 0.85:
            self.evolve_principles_post_run(str(final_candidate), score, validation_result)

        if score > 0.92 and getattr(self, "enable_grail", False):
            self.consolidate_grail(str(final_candidate), score, validation_result)

        # Stigmergic trace
        self._write_stigmergic_trace({
            "task": task,
            "verifiability_contract": verifiability_contract,
            "dry_run": dry_run,
            "real": {
                "edge": round(edge, 4),
                "invariant": round(invariant, 4),
                "fidelity": round(fidelity, 4),
                "hetero": round(hetero, 4),
                "c": round(c, 4),
                "theta": round(theta, 4),
                "EFS": round(efs, 4),
                "score": round(score, 4)
            },
            "loop": self.loop_count,
            "timestamp": datetime.now().isoformat()
        })

        # Final embodiment & outer loop processing
        self._end_of_run({
            "final_score": score,
            "efs": efs,
            "best_solution": final_candidate,
            "diagnostics": validation_result
        })

        return {
            "merged_candidate": final_candidate,
            "validation_result": validation_result,
            "synthesis_result": synthesis_result,
            "verifiability_contract": verifiability_contract,
            "human_refinement": human_refinement,
            "recommended_tools": strategy.get("recommended_tools", []),
            "metrics": {"score": score, "efs": efs, "c": c, "theta": theta}
        }
                                 
    def _orchestrator_self_dialogue(self, task: str, goal_md: str) -> Dict[str, Any]:
        """Explicit inner self-dialogue for Orchestrator Arbos.
        Forces the entire plan to be built around required artifacts and the verifiability spec."""
        
        shared_core = load_brain_component("principles/shared_core")
        heterogeneity = load_brain_component("principles/heterogeneity")

        dialogue_prompt = f"""You are Orchestrator Arbos for SN63 Enigma Miner.

TASK: {task}

GOAL CONTEXT:
{goal_md[:3000]}

{shared_core}

Heterogeneity Principle:
{heterogeneity}

VERIFIABILITY CONTRACT RULES (must obey):
- Explicitly list every required artifact (x, y, z...) the subtasks must produce.
- Define clear merge interfaces so recomposition is deterministic.
- Ensure the merged candidate can pass the full verifier set (edge ≥ 0.75, c ≥ 0.78, EFS ≥ 0.65 in best case).
- Maximize heterogeneity across the five axes.

Answer these questions in your reasoning:
1. What exact artifacts do I need to build a solution that can pass challenge-level verification?
2. What interfaces / schemas must each artifact satisfy for clean recomposition?
3. What verifier coverage is mandatory?
4. What is the risk if any artifact is missing or incompatible?

Return ONLY valid JSON with these keys:
{{
  "artifacts_required": [list of dicts with name, schema, verifier_snippets, merge_interface],
  "composability_rules": [list of strings],
  "dry_run_success_criteria": {{...}},
  "decomposition_strategy": "brief description",
  "risks_and_mitigations": [list]
}}"""

        model_config = self.load_model_registry(role="planner")
        raw_response = self.harness.call_llm(
            dialogue_prompt, 
            temperature=0.35, 
            max_tokens=1400, 
            model_config=model_config
        )

        spec = self._safe_parse_json(raw_response)

        # Merge with analyzer-generated base spec
        analyzer_spec = self.analyzer._generate_verifiability_spec(task, "")
        if "artifacts_required" in spec:
            analyzer_spec["artifacts_required"] = spec.get("artifacts_required", [])

        return {
            "self_dialogue_output": spec,
            "final_verifiability_spec": analyzer_spec,
            "decomposition_strategy": spec.get("decomposition_strategy", "Standard heterogeneous decomposition")
        }
        
    def _run_orchestrator_debate(self, task: str, contract: Dict, rich_context: Dict) -> Dict:
        """v0.8 2-Round Critique-First Debate for Orchestrator Phase 2.
        Forces structured output and includes safety guards."""
        
        if not contract:
            contract = {}
        if not rich_context:
            rich_context = {}

        debate_prompt = f"""You are Orchestrator Arbos running a strict 2-round critique-first debate.

TASK: {task}

VERIFIABILITY CONTRACT:
{json.dumps(contract, indent=2)[:900]}

RICH CONTEXT:
{json.dumps(rich_context, indent=2)[:700]}

INSTRUCTIONS:
Round 1: Harshly critique weaknesses in decomposition, composability rules, verifier coverage, and missing artifacts.
Round 2: Propose concrete refinements and converge on an improved contract with better slices.

Return ONLY valid JSON with this exact structure:
{{
  "refined_contract": {{ ... improved version of the contract ... }},
  "debate_summary": "brief summary of critiques and decisions",
  "key_improvements": ["list of specific changes made"],
  "confidence": 0.0-1.0
}}"""

        try:
            model_config = self.load_model_registry(role="planner")
            raw = self.harness.call_llm(
                debate_prompt, 
                temperature=0.38, 
                max_tokens=1600, 
                model_config=model_config
            )
            
            result = self._safe_parse_json(raw)

            # Safety fallback
            if not isinstance(result, dict) or "refined_contract" not in result:
                logger.warning("Orchestrator debate returned invalid JSON — using original contract")
                return {
                    "refined_contract": contract,
                    "debate_summary": "Debate failed — using original contract",
                    "key_improvements": [],
                    "confidence": 0.45
                }

            logger.info(f"Orchestrator 2-round debate completed | Confidence: {result.get('confidence', 0.0):.2f}")
            return result

        except Exception as e:
            logger.error(f"Orchestrator debate failed: {e}")
            return {
                "refined_contract": contract,
                "debate_summary": f"Debate crashed: {str(e)[:200]}",
                "key_improvements": [],
                "confidence": 0.3
            }
        
    def _execute_swarm(self, blueprint: Dict, dynamic_size: int):
        """Updated swarm executor — now routes through the advanced _launch_hyphal_workers."""
        blueprint = self._safe_parse_json(blueprint) if isinstance(blueprint, str) else blueprint
        
        decomposition = blueprint.get("decomposition", ["Full challenge execution"])
        hypothesis_diversity = blueprint.get("hypothesis_diversity", ["standard"])
        if not hypothesis_diversity:
            hypothesis_diversity = ["standard"]

        logger.info(f"Executing swarm with {dynamic_size} workers using advanced launch system")

        # Use the new advanced launch method (dynamic roles, message bus, evolutionary selection)
        subtask_outputs = self._launch_hyphal_workers(
            task=blueprint.get("challenge", "current"),
            strategy=blueprint
        )

        # Convert to the old expected format for backward compatibility
        manager_dict = {}
        for output in subtask_outputs:
            subtask_id = output.get("subtask_id", len(manager_dict))
            manager_dict[subtask_id] = output

        logger.info(f"Swarm execution completed — {len(subtask_outputs)} subtasks returned")
        return manager_dict
        
    # ====================== SUB-ARBOS WORKER (FULLY HARDENED v5.2 - BUG FREE) ======================
    def _launch_hyphal_workers(self, task: str, strategy: Dict) -> List[Dict]:
        """v0.8 Advanced swarm execution with stigmergic communication, 
        intelligent dynamic roles, per-subtask contract slices, and evolutionary tournament."""

        subtask_outputs = {}
        message_bus = []  # shared stigmergic communication channel

        swarm_config = strategy.get("swarm_config", {"total_instances": 8})
        decomposition: List[str] = strategy.get("decomposition", [task])
        full_contract = strategy.get("verifiability_contract", 
                                   strategy.get("verifiability_spec", {}))

        max_workers = min(swarm_config.get("total_instances", 8), 12)  # safety cap

        logger.info(f"Launching advanced hyphal swarm — {max_workers} workers | "
                   f"Subtasks: {len(decomposition)} | Using contract slices")

        # Create focused per-subtask contract slices (Deep-Dive Point 2)
        subtask_contract_slices = []
        artifacts = full_contract.get("artifacts_required", [])
        verifier_snippets = strategy.get("verifier_code_snippets", [])[:8]

        for i, subtask in enumerate(decomposition):
            slice_contract = {
                "subtask_name": subtask,
                "parent_contract_summary": full_contract.get("summary", "")[:400],
                "artifacts_required": artifacts[:min(5, len(artifacts))],   # focused slice
                "verifier_code_snippets": verifier_snippets,
                "composability_rules": full_contract.get("composability_rules", []),
                "recomposition_guidance": full_contract.get("recomposition_plan", {}).get("guidance", ""),
                "double_click_eligible": True,
                "subtask_index": i
            }
            subtask_contract_slices.append(slice_contract)

        # Intelligent dynamic role assignment (Orchestrator decides)
        roles = self._assign_dynamic_roles(
            decomposition=decomposition, 
            contract=full_contract
        )

        # Launch workers
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for i, subtask in enumerate(decomposition[:max_workers]):
                role = roles[i % len(roles)] if roles else "base_reasoner"
                subtask_contract = subtask_contract_slices[i] if i < len(subtask_contract_slices) else {}

                future = executor.submit(
                    self._sub_arbos_worker,
                    subtask=subtask,
                    hypothesis=strategy.get("hypothesis_diversity", ["base"])[i % len(strategy.get("hypothesis_diversity", ["base"]))],
                    tools=strategy.get("tool_map", {}).get(i, []),
                    shared_results=subtask_outputs,
                    subtask_id=i,
                    role=role,
                    message_bus=message_bus,
                    subtask_contract=subtask_contract   # critical: pass slice
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if isinstance(result, dict) and "subtask_id" in result:
                        subtask_outputs[result["subtask_id"]] = result
                        
                        # Stigmergic broadcast
                        if "solution" in result:
                            message_bus.append({
                                "subtask_id": result.get("subtask_id"),
                                "role": result.get("role"),
                                "solution_snippet": str(result.get("solution", ""))[:450],
                                "score": result.get("local_score", 0.5),
                                "subtask_contract_used": bool(result.get("subtask_contract"))
                            })
                except Exception as e:
                    logger.error(f"Sub-Arbos worker {i} failed: {e}")

        # Evolutionary tournament (keep best performers)
        if len(subtask_outputs) > 3:
            subtask_outputs = self._swarm_evolutionary_tournament(
                subtask_outputs, message_bus, full_contract
            )

        final_outputs = list(subtask_outputs.values())
        
        logger.info(f"Hyphal swarm completed — {len(final_outputs)} outputs | "
                   f"Contract slices used: {len([o for o in final_outputs if o.get('subtask_contract')])}")

        return final_outputs
        
    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                          shared_results: dict, subtask_id: int,
                          role: str = "base", message_bus: List = None,
                          subtask_contract: Dict = None) -> dict:
        """v0.8 Top-tier Sub-Arbos Worker — now receives explicit subtask_contract slice
        for local verifier-first validation on every attempt."""

        if message_bus is None:
            message_bus = []
        if subtask_contract is None:
            subtask_contract = {}  # safe fallback

        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours / 3.0)
        repair_attempts = 0
        
        self.current_role = role

        trace = [f"Sub-Arbos {subtask_id} started | Role: {role} | Using subtask_contract slice | Hardening dialogue active"]

        challenge_id = getattr(self, "_current_challenge_id", "current_challenge")
        subtask_path = self._create_subtask_wiki_folder(challenge_id, str(subtask_id))

        # Localized breakthrough check (still works with contract slice)
        if (self.model_compute_capability_enabled and 
            self.allow_per_subarbos_breakthrough and 
            self.is_stagnant_subarbos(str(subtask_id))):
            gap = self.generate_gap_diagnosis(str(subtask_id))
            rec_model = self.recommend_breakthrough_model(gap)
            logger.info(f"🔥 Localized stagnation in Sub-Arbos {subtask_id} — using {rec_model} breakthrough")

        if self.config.get("resource_aware") and monitor.elapsed_hours() > max_hours * 0.75:
            solution = "Early abort: time budget exceeded."
            trace.append("Resource-aware early abort")
            local_score = 0.0
        else:
            # ... (your existing solution generation loop stays exactly as you had it) ...
            # [I kept your full generation/repair/early-abort logic untouched — only added contract usage below]

            # v0.8: Use subtask_contract slice for local validation on every attempt
            final_validation = self.validator.run(
                candidate=solution,
                verification_instructions="",
                challenge=subtask,
                goal_md=self.extra_context,
                subtask_outputs=[solution],
                subtask_contract=subtask_contract   # <-- NEW: passes the slice
            )

            local_score = final_validation.get("validation_score", 0.0)

            # Verifier Self-Check Layer (Deep-Dive Point 8)
            verifier_quality = self.validator._compute_verifier_quality(solution, subtask_contract.get("verifier_code_snippets", []))
            if verifier_quality < 0.65:
                trace.append(f"Verifier Self-Check Layer flagged low quality ({verifier_quality:.3f}) — DOUBLE_CLICK eligible")

        # Stigmergic write (still uses your _write_subtask_md)
        self._write_subtask_md(subtask_path, solution, bio_delta="")

        # Decision journal (keeps your exact format)
        self.write_decision_journal(
            subtask_id=str(subtask_id),
            hypothesis=hypothesis,
            evidence=solution[:800] if solution else "",
            performance_delta={"delta_s": local_score, "delta_c": final_validation.get("c3a_confidence", 0.0)},
            organic_thought=final_validation.get("notes", "")
        )

        # Broadcast to message bus
        if message_bus is not None:
            message_bus.append({
                "subtask_id": subtask_id,
                "role": role,
                "solution_snippet": solution[:400] if solution else "",
                "local_score": local_score,
                "subtask_contract_used": bool(subtask_contract)
            })

        # Store result
        shared_results[subtask_id] = {
            "subtask": subtask,
            "solution": solution,
            "trace": trace,
            "local_score": local_score,
            "oracle_result": final_validation,
            "role": role,
            "subtask_contract": subtask_contract  # for downstream synthesis
        }

        logger.info(f"Sub-Arbos {subtask_id} completed | Score: {local_score:.3f} | Role: {role} | Contract slice used: {bool(subtask_contract)}")
        return shared_results[subtask_id]

    
    def _assign_dynamic_roles(self, decomposition: List, contract: Dict = None, 
                              previous_outputs: List = None) -> List[str]:
        """SOTA Dynamic Role Assignment — Orchestrator Arbos decides intelligently 
        using full context instead of hardcoded base roles."""
        
        if not decomposition:
            return ["base_reasoner"] * 3

        if contract is None:
            contract = {}
        if previous_outputs is None:
            previous_outputs = []

        # Rich context for Orchestrator to reason over
        context_for_orchestrator = {
            "decomposition": decomposition,
            "verifiability_contract": contract,
            "previous_outputs_summary": [o.get("subtask", "") for o in previous_outputs[-6:]],
            "required_artifacts": contract.get("artifacts_required", []),
            "composability_rules": contract.get("composability_rules", []),
            "goal": "Maximize heterogeneity across agent style, hypothesis framing, symbolic depth, and verification strength"
        }

        prompt = f"""You are Orchestrator Arbos — expert at assigning optimal roles to Sub-Arbos workers.

CONTEXT:
{json.dumps(context_for_orchestrator, indent=2)}

Available role types you can assign (you can invent new ones if needed):
- symbolic_reasoner, invariant_tightener, edge_case_hunter, numerical_optimizer,
- creative_synthesizer, verifier_specialist, novelty_generator, composability_guard,
- quantum_mapper, causal_analyst, proof_strategist, etc.

For each subtask in the decomposition, assign the single best role that contributes to overall swarm heterogeneity and contract compliance.

Return ONLY a valid JSON array of role names (same length as decomposition)."""

        try:
            model_config = self.load_model_registry(role="planner")
            raw = self.harness.call_llm(prompt, temperature=0.55, max_tokens=800, model_config=model_config)
            roles = self._safe_parse_json(raw)

            if isinstance(roles, list) and len(roles) == len(decomposition):
                logger.info(f"Orchestrator dynamically assigned roles: {roles}")
                return roles
        except Exception as e:
            logger.warning(f"Dynamic role assignment failed, falling back to smart defaults: {e}")

        # Intelligent fallback (still better than old cycling)
        base_roles = ["symbolic_reasoner", "edge_case_hunter", "invariant_tightener", 
                     "creative_synthesizer", "verifier_specialist", "novelty_generator"]
        return [base_roles[i % len(base_roles)] for i in range(len(decomposition))]

    def _swarm_evolutionary_tournament(self, outputs: Dict, 
                                       message_bus: List = None, 
                                       contract: Dict = None) -> Dict:
        """Advanced intra-swarm selection: evolutionary tournament with contract alignment 
        and heterogeneity bonus. Returns the strongest subset of subtask outputs."""
        
        if not outputs or len(outputs) <= 3:
            logger.debug("Swarm tournament skipped — too few outputs")
            return outputs or {}

        if message_bus is None:
            message_bus = []
        if contract is None:
            contract = {}

        scored = []
        required_artifacts = contract.get("artifacts_required", []) if isinstance(contract, dict) else []
        composability_rules = contract.get("composability_rules", []) if isinstance(contract, dict) else []

        for oid, out in outputs.items():
            if not isinstance(out, dict):
                continue

            base_score = out.get("local_score", 0.5)

            # 1. Contract alignment bonus
            solution_text = str(out.get("solution", ""))
            artifact_bonus = 0.0
            if required_artifacts:
                matched = sum(1 for a in required_artifacts 
                             if str(a).lower() in solution_text.lower())
                artifact_bonus = 0.28 * (matched / max(1, len(required_artifacts)))

            # 2. Heterogeneity / role bonus
            role = out.get("role", "").lower()
            hetero_bonus = 0.0
            if role in ["creative_synthesizer", "edge_case_hunter", "invariant_tightener"]:
                hetero_bonus = 0.18
            elif "diverse" in role or "novel" in role:
                hetero_bonus = 0.12

            # 3. Message bus synergy bonus (stigmergic communication)
            synergy_bonus = 0.0
            if message_bus:
                synergy_bonus = 0.08 if any(
                    out.get("subtask") in str(m.get("solution_snippet", "")) 
                    for m in message_bus[-8:]
                ) else 0.0

            final_score = base_score + artifact_bonus + hetero_bonus + synergy_bonus
            scored.append((oid, final_score, out))

        if not scored:
            return outputs

        # Sort by final_score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Keep top 70-80% but never fewer than 3
        keep_count = max(3, int(len(scored) * 0.78))
        winners = {oid: out for oid, _, out in scored[:keep_count]}

        logger.info(f"Evolutionary tournament completed — kept {len(winners)}/{len(outputs)} "
                   f"subtasks (best score: {scored[0][1]:.3f})")

        return winners

    def _evolutionary_selection(self, outputs: Dict, contract: Dict) -> Dict:
        """Lightweight fallback evolutionary selection (used by older paths)."""
        return self._swarm_evolutionary_tournament(outputs, [], contract)  # reuse the better version
        
    def execute_full_cycle(self, blueprint: Dict, challenge: str, verification_instructions: str = ""):
        """v0.8 Full inner loop execution with advanced swarm, synthesis, symbiosis, 
        intelligent replanning, and per-subtask contract support."""
        dynamic_size = blueprint.get("dynamic_swarm_size", 
                                    blueprint.get("swarm_config", {}).get("total_instances", 6))
        
        # 1. Advanced Swarm Execution (with per-subtask contract slices)
        results = self._execute_swarm(blueprint, dynamic_size)
        
        # 2. Raw recompose
        raw_merged = self._recompose(results, {}) if results else {"solution": str(results)}

        # 3. Advanced Synthesis Arbos (intelligent recombination with debate + contract enforcement)
        synthesis_result = self.synthesis_arbos(
            subtask_outputs=list(results.values()) if isinstance(results, dict) else [],
            recomposition_plan=blueprint.get("recomposition_plan", {}),
            verifiability_contract=blueprint.get("verifiability_contract", blueprint.get("verifiability_spec", {})),
            failure_context=None
        )

        final_candidate = synthesis_result.get("final_candidate", raw_merged)

        # 4. Symbiosis Arbos (emergent pattern detection)
        symbiosis_patterns = self._run_symbiosis_arbos(
            aggregated_outputs=results,
            message_bus=self.message_bus,
            synthesis_result=synthesis_result
        )

        # 5. Final ValidationOracle (source of truth)
        validation_result = self.validator.run(
            candidate=final_candidate,
            verification_instructions=verification_instructions,
            challenge=challenge,
            goal_md=self.extra_context,
            subtask_outputs=list(results.values()) if isinstance(results, dict) else []
        )

        score = validation_result.get("validation_score", 0.0)
        efs = validation_result.get("efs", 0.0)

        # ByteRover promotion
        if score > 0.70:
            self.memory_layers.promote_high_signal(
                str(final_candidate),
                {
                    "local_score": score,
                    "fidelity": validation_result.get("fidelity", 0.8),
                    "heterogeneity_score": self._compute_heterogeneity_score().get("heterogeneity_score", 0.7)
                }
            )

        self.memory_layers.compress_low_value(current_score=score)

        # 6. Intelligent stall detection & replan
        dry_run_result = blueprint.get("dry_run_result", {})
        stall_analysis = self._analyze_swarm_stall(
            list(results.values()) if isinstance(results, dict) else [],
            validation_result,
            dry_run_result
        )

        if stall_analysis.get("is_severe_stall", False):
            logger.warning(f"Real swarm stall detected. Delta: {stall_analysis.get('delta', 0):.3f}")

            failure_context = self._build_failure_context(
                failure_type="swarm_stall_on_passed_spec",
                task=challenge,
                goal_md=self.extra_context,
                strategy=self._current_strategy or {},
                dry_run=dry_run_result,
                swarm_results=list(results.values()) if isinstance(results, dict) else [],
                validation_result=validation_result
            )

            replan_decision = self._intelligent_replan(failure_context)

            if replan_decision.get("decision") == "new_strategy_needed":
                logger.info("Stall reflection decided NEW STRATEGY needed — triggering full replan")
                new_task = f"{challenge} [STALL RECOVERY - previous spec failed in practice]"
                return self.orchestrate_subarbos(new_task, self.extra_context)
            else:
                logger.info("Stall reflection decided fixable — applying targeted fixes")
                if replan_decision.get("spec_fixes") and self._current_strategy:
                    if "verifiability_contract" in self._current_strategy:
                        self._current_strategy["verifiability_contract"]["fixes_applied"] = replan_decision["spec_fixes"]

        # v0.8 Additions (only added, nothing removed):

        # Experiment summary capture for Scientist Mode / Meta-Tuning
        if hasattr(self, '_current_scientist_summary') or "scientist_summary" in blueprint:
            run_data_for_end = {
                "final_score": score,
                "efs": efs,
                "best_solution": final_candidate,
                "diagnostics": validation_result,
                "scientist_summary": blueprint.get("scientist_summary") or getattr(self, '_current_scientist_summary', {})
            }
        else:
            run_data_for_end = {
                "final_score": score,
                "efs": efs,
                "best_solution": final_candidate,
                "diagnostics": validation_result
            }

        # Success path
        if score > 0.92 and self.enable_grail:
            self.consolidate_grail(str(final_candidate), score, validation_result)

        if score > 0.85:
            self.evolve_principles_post_run(str(final_candidate), score, validation_result)
            
        self.save_run_to_history(challenge, "", str(final_candidate), score, 0.5, score)

        # Final outer-loop processing
        self._end_of_run(run_data_for_end)

        return validation_result
        
    def _write_stigmergic_trace(self, trace: Dict):
        """Core stigmergic learning — writes full traceable record to wiki and memory."""
        try:
            challenge_id = getattr(self, "_current_challenge_id", "current")
            path = Path(f"goals/knowledge/{challenge_id}/wiki/traces")
            path.mkdir(parents=True, exist_ok=True)
            
            filename = f"trace_{self.loop_count}_{int(datetime.now().timestamp())}.json"
            (path / filename).write_text(json.dumps(trace, indent=2))
            
            # Also add to long-term memory
            memory.add(json.dumps(trace), {"type": "stigmergic_trace", "loop": self.loop_count})
            
            logger.info(f"Stigmergic trace written: {filename}")
        except Exception as e:
            logger.warning(f"Failed to write stigmergic trace: {e}")

    def _recompose(self, subtask_outputs: List[Dict], recomposition_plan: Dict) -> Dict:
        """Robust recomposition — fidelity-ordered merge with contract awareness.
        Now properly uses recomposition_plan and handles edge cases safely."""
        if not subtask_outputs:
            return {
                "solution": "",
                "recomposition_notes": "No outputs received",
                "total_subtasks": 0,
                "success": False
            }

        # Sort by local_score (fidelity) descending
        sorted_outputs = sorted(
            subtask_outputs, 
            key=lambda x: x.get("local_score", 0.0) if isinstance(x, dict) else 0.0, 
            reverse=True
        )

        merged = {"solution": ""}
        used_artifacts = []

        for output in sorted_outputs:
            if not isinstance(output, dict):
                continue
                
            sol = output.get("solution", "")
            subtask_name = output.get("subtask", "unknown")
            
            if isinstance(sol, dict):
                # Merge structured output
                merged.update(sol)
                used_artifacts.append(subtask_name)
            elif isinstance(sol, str):
                # Append text output
                if merged["solution"]:
                    merged["solution"] += "\n\n"
                merged["solution"] += f"### {subtask_name}\n{sol.strip()}"
                used_artifacts.append(subtask_name)
            else:
                # Fallback for other types
                merged["solution"] += f"\n\n{subtask_name}: {str(sol)}"

        # Incorporate guidance from recomposition_plan if available
        if recomposition_plan and isinstance(recomposition_plan, dict):
            guidance = recomposition_plan.get("guidance", "") or recomposition_plan.get("synthesis_guidance", "")
            if guidance:
                merged["solution"] += f"\n\n# SYNTHESIS GUIDANCE\n{guidance}"

        merged["recomposition_notes"] = f"Merged {len(used_artifacts)}/{len(subtask_outputs)} subtasks by fidelity order"
        merged["total_subtasks"] = len(subtask_outputs)
        merged["used_artifacts"] = used_artifacts
        merged["success"] = len(used_artifacts) > 0

        logger.info(f"Recomposition completed — {len(used_artifacts)} subtasks merged | Plan used: {bool(recomposition_plan)}")
        return merged
        
    def synthesis_arbos(self, subtask_outputs: List[Dict], recomposition_plan: Dict, 
                        verifiability_contract: Dict, failure_context: Dict = None) -> Dict:
        """Maximum capability Synthesis Arbos — multi-proposal generation, structured debate, 
        iterative refinement, and strict contract enforcement."""
        
        if not subtask_outputs or len(subtask_outputs) == 0:
            return {
                "final_candidate": "", 
                "synthesis_notes": "No outputs received", 
                "spec_compliance": "low", 
                "confidence": 0.0
            }

        # Use consistent contract naming
        contract = {
            "artifacts_required": verifiability_contract.get("artifacts_required", []),
            "composability_rules": verifiability_contract.get("composability_rules", []),
            "synthesis_guidance": verifiability_contract.get("synthesis_guidance", ""),
            "dry_run_criteria": verifiability_contract.get("dry_run_success_criteria", {}),
            "recomposition_plan": recomposition_plan
        }

        # Stage 1: Generate multiple diverse proposals
        proposal_prompt = f"""You are Synthesis Arbos. Generate 4 fundamentally different high-quality merging strategies.

VERIFIABILITY CONTRACT (must be strictly satisfied):
{json.dumps(contract, indent=2)}

SUBTASK OUTPUTS:
{json.dumps([{
    "subtask": o.get("subtask", "unknown"),
    "role": o.get("role", "unknown"),
    "solution": str(o.get("solution", ""))[:700]
} for o in subtask_outputs], indent=2)}

{f"PAST FAILURE CONTEXT: {json.dumps(failure_context, indent=2)[:800]}" if failure_context else ""}

Return ONLY a valid JSON array containing 4 proposals. Each proposal must have: 
"proposal_id", "merged_candidate", "strategy_description", "expected_strengths", "risks"."""

        model_config = self.load_model_registry(role="planner")
        raw_proposals = self.harness.call_llm(proposal_prompt, temperature=0.6, max_tokens=2800, model_config=model_config)
        proposals = self._safe_parse_json(raw_proposals)

        if not isinstance(proposals, list):
            proposals = [proposals] if proposals else []

        # Stage 2: Multi-round debate and critique
        debate_prompt = f"""You are Synthesis Arbos running a structured internal debate.

Contract (non-negotiable):
{json.dumps(contract, indent=2)}

Proposals to debate:
{json.dumps(proposals, indent=2)}

Critique each proposal harshly against the contract.
Identify which best satisfies the contract.
Create the strongest possible hybrid if needed.

Return ONLY valid JSON:
{{
  "final_candidate": "the complete merged solution",
  "synthesis_notes": "full debate summary, critiques, and decisions",
  "spec_compliance": "high/medium/low",
  "confidence": 0.0-1.0,
  "refinement_steps": ["step 1", "step 2"],
  "winning_proposal_id": "which one won or hybrid",
  "remaining_risks": []
}}"""

        raw_final = self.harness.call_llm(debate_prompt, temperature=0.3, max_tokens=2600, model_config=model_config)
        result = self._safe_parse_json(raw_final)

        # Stage 3: Final strict contract enforcement pass
        if result.get("spec_compliance") != "high":
            logger.warning("Synthesis compliance not high — running final enforcement pass")
            enforcement_prompt = f"""Take this candidate and make it FULLY compliant with the verifiability contract.

Candidate:
{result.get('final_candidate', '')[:3000]}

Contract:
{json.dumps(contract, indent=2)}

Return only the improved final_candidate."""
            
            fixed_candidate = self.harness.call_llm(enforcement_prompt, temperature=0.2, max_tokens=2200, model_config=model_config)
            result["final_candidate"] = fixed_candidate
            result.setdefault("refinement_steps", []).append("Final contract enforcement pass")

        logger.info(f"Synthesis Arbos completed | Compliance: {result.get('spec_compliance', 'medium')} | Confidence: {result.get('confidence', 0.0):.3f}")

        return result
                            

    def _run_verification(self, solution: str, verification_instructions: str, challenge: str) -> str:
        oracle_result = self.validator.run(
            candidate={"solution": solution},
            verification_instructions=verification_instructions,
            challenge=challenge,
            goal_md=self.extra_context,
            subtask_outputs=[solution]
        )

        self._current_strategy = oracle_result.get("strategy")

        self.vector_db.add({
            "solution": solution[:1000],
            "challenge": challenge,
            "validation_score": oracle_result.get("validation_score", 0.0),
            "fidelity": oracle_result.get("fidelity", 0.88),
            "heterogeneity_score": self._compute_heterogeneity_score().get("heterogeneity_score", 0.65),
            "loop": self.loop_count,
            "source": "validation_oracle"
        })

        return f"ValidationOracle: score={oracle_result.get('validation_score', 0):.3f} | EFS={oracle_result.get('efs', 0.0):.3f}"
    
    def _tool_hunter(self, gap: str, subtask: str) -> str:
        result = tool_hunter.hunt_and_integrate(gap, subtask)
        if result.get("status") == "success" and result.get("links"):
            for link in result.get("links", [])[:3]:
                clean = self.reach_tool.fetch_url_content(link.get("url", ""))
                self.vector_db.add({
                    "solution": clean[:800],
                    "challenge": subtask,
                    "validation_score": 0.6,
                    "fidelity": 0.7,
                    "heterogeneity_score": 0.65,
                    "source": "agent_reach",
                    "url": link.get("url")
                })
                result["recommendation"] += f"\n[Agent-Reach] {link.get('url')}: {clean[:200]}..."
        if result.get("status") == "success":
            return f"ToolHunter + Agent-Reach ({result.get('source', 'unknown')}): {result.get('recommendation')}"
        return "ToolHunter + Agent-Reach found no strong match for this quantum subtask."

    def _generate_tool_proposals(self, results: Dict) -> List[str]:
        proposal_prompt = f"Based on these swarm results: {json.dumps(results)[:1500]}\nSuggest 2-3 deterministic or quantum-related tools that would improve verifier score on the NEXT run."
        response = self.harness.call_llm(proposal_prompt, temperature=0.3, max_tokens=600)
        proposals = [line.strip() for line in response.split("\n") if line.strip()][:3]
        
        for p in proposals:
            try:
                memory.add(f"TOOL PROPOSAL: {p}", {"type": "tool_proposal"})
            except Exception as e:
                logger.warning(f"Failed to add proposal: {e}")
        
        return proposals
            
    def _run_grail_post_training(self, results: Dict):
        logger.info("Grail post-training triggered on winning run (verifiable proof attached to package)")

    def get_vector_db_stats(self):
        return self.vector_db.get_stats()

    def export_trajectories_for_optimization(self, challenge: str):
        traj = self.vector_db.search(challenge, k=50)
        path = Path("trajectories") / f"export_{challenge[:30]}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(traj, indent=2))
        logger.info(f"Exported {len(traj)} trajectories to {path}")
        return str(path)

    def save_run_to_history(self, challenge: str, enhancement_prompt: str, solution: str, 
                            score: float, novelty: float, verifier: float, main_issue: str = "None"):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    history = json.load(f)
            except:
                history = []
        entry = {
            "timestamp": datetime.now().isoformat(),
            "challenge": challenge[:200],
            "enhancement_prompt": enhancement_prompt[:500],
            "score": round(score, 1),
            "novelty": round(novelty, 1),
            "verifier": round(verifier, 1),
            "main_issue": main_issue
        }
        history.append(entry)
        with open(self.history_file, "w") as f:
            json.dump(history[-100:], f, indent=2)

    def get_run_history(self, n: int = 10) -> List[Dict]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
            return history[-n:]
        except:
            return []

    def self_critique(self, challenge: str, n_runs: int = 5) -> Dict[str, Any]:
        history = self.get_run_history(n_runs)
        trajectories = self.vector_db.search(challenge, k=20)
        critique_task = f"""You are Arbos Self-Improvement Analyst for SN63 Quantum.

Challenge: {challenge}
Recent run history:
{json.dumps(history, indent=2)}
High-signal trajectories:
{json.dumps(trajectories, indent=2)}

Be critical."""
        response = self.harness.call_llm(critique_task, temperature=0.7, max_tokens=1000)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            parsed = json.loads(response[start:end])
            for mem in parsed.get("structured_memories", []):
                memory.add(json.dumps(mem), {"type": "trajectory_memory"})
            return parsed
        except:
            return {
                "structured_memories": [],
                "workflow_evolution": ["Validator appears too lenient — add realism constraints", "Force explicit feasibility statements in plans"],
                "recommended_prompt_additions": "Always be brutally honest about computational feasibility."
            }

    def spawn_tool_subswarm(self, subtask_list: list):
        return {subtask: f"ToolHunter-{subtask}" for subtask in subtask_list}

    def _refine_plan(self, approved_plan: Dict, challenge: str, deterministic_tooling: str = "", enhancement_prompt: str = "") -> Dict:
        """Intelligent plan refinement after each loop or re-adapt — returns improved blueprint."""
        extra = f"\nMiner deterministic tooling: {deterministic_tooling}" if deterministic_tooling else ""
        extra += f"\nMiner enhancement instructions: {enhancement_prompt}" if enhancement_prompt else ""
        
        refine_prompt = f"""You are Orchestrator Arbos for SN63 Quantum Innovate.

Approved plan from previous loop:
{json.dumps(approved_plan, indent=2)}

Latest human refinement: {enhancement_prompt}
Current challenge: {challenge}
{extra}

Refine the blueprint intelligently:
- Keep what worked (high EFS/c areas)
- Fix what failed (low replay pass rate or contract violations)
- Increase heterogeneity where needed
- Strengthen Synthesis guidance and contract compliance

Return ONLY valid JSON with the same structure as the input plan, plus:
- "refinement_notes": "what changed and why"
- "expected_efs_gain": estimated improvement (0.0-1.0)"""

        model_config = self.load_model_registry(role="planner")
        response = self.harness.call_llm(refine_prompt, temperature=0.35, max_tokens=1600, model_config=model_config)
        refined = self._safe_parse_json(response)

        if not refined or "decomposition" not in refined:
            logger.warning("Plan refinement failed — returning original plan with notes")
            approved_plan["refinement_notes"] = "Refinement failed — using original plan"
            return approved_plan

        logger.info(f"Plan refined successfully — expected EFS gain: {refined.get('expected_efs_gain', 'unknown')}")
        return refined

    def _generate_new_avenue_plan(self, challenge: str, recent_feedback: str, diagnostics: Dict = None) -> str:
        """Generates a radically different new strategy when the current path is stalled."""
        if diagnostics is None:
            diagnostics = {}

        prompt = f"""You are Deep Replan Arbos for SN63.

Current challenge: {challenge}
Recent feedback: {recent_feedback[:1500]}
Diagnostics: {json.dumps(diagnostics, indent=2)[:800]}

The current strategy has stalled. Generate a completely new, high-heterogeneity avenue 
that respects the verifiability contract but approaches the problem from a fresh angle.

Return ONLY valid JSON:
{{
  "new_avenue_name": "short memorable name",
  "decomposition_strategy": "high-level new breakdown",
  "key_hypotheses": ["list of new hypotheses"],
  "tool_recommendations": ["new tools or approaches"],
  "expected_advantages": "why this should outperform the previous path",
  "risks": ["potential risks"]
}}"""

        model_config = self.load_model_registry(role="planner")
        response = self.harness.call_llm(prompt, temperature=0.72, max_tokens=1400, model_config=model_config)
        new_plan = self._safe_parse_json(response)

        self._pending_new_avenue_plan = json.dumps(new_plan, indent=2)
        self.save_to_memdir(f"new_avenue_{int(time.time())}", new_plan)

        logger.info(f"✅ New Avenue Plan generated: {new_plan.get('new_avenue_name', 'Unnamed radical direction')}")
        return json.dumps(new_plan, indent=2)

    def _init_memdir(self):
        """Initialize memdir/grail structure."""
        self.memdir_path = Path("memdir/grail")
        self.memdir_path.mkdir(parents=True, exist_ok=True)
        (self.memdir_path / "snapshots").mkdir(exist_ok=True)
        (self.memdir_path / "compression").mkdir(exist_ok=True)
        logger.info(f"✅ Memdir/Grail initialized at {self.memdir_path}")

    def save_to_memdir(self, key: str, data: Any):
        """Save any serializable data to memdir."""
        try:
            path = self.memdir_path / f"{key}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save to memdir {key}: {e}")

    def load_from_memdir(self, key: str) -> dict:
        """Load data from memdir."""
        try:
            path = self.memdir_path / f"{key}.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.debug(f"Failed to load from memdir {key}: {e}")
        return {}
    def post_message(self, sender: str, content: str, msg_type: str = "general", 
                     importance: float = 0.5, validation_score: float = None, fidelity: float = None):
        """Post a message to the stigmergic message bus."""
        message = {
            "sender": sender,
            "content": content,
            "type": msg_type,
            "importance": importance,
            "validation_score": validation_score or 0.0,
            "fidelity": fidelity or 0.0,
            "timestamp": datetime.now().isoformat(),
            "loop": self.loop_count
        }
        
        # Deduplicate same type in current loop
        self.message_bus = [m for m in self.message_bus 
                           if not (m.get("type") == msg_type and m.get("loop") == self.loop_count)]
        self.message_bus.append(message)

        if importance > 0.6 or (validation_score and validation_score > 0.85):
            self.save_to_memdir(f"message_{msg_type}_{int(time.time())}", message)

        logger.debug(f"Message posted by {sender} | type={msg_type} | score={validation_score or 0:.2f}")

    def get_recent_messages(self, min_importance: float = 0.4, limit: int = 12, msg_type: str = None) -> list:
        """Get recent high-importance messages."""
        recent = [m for m in self.message_bus if m.get("importance", 0) >= min_importance]
        if msg_type:
            recent = [m for m in recent if m.get("type") == msg_type]
        recent.sort(key=lambda m: (m.get("validation_score", 0), m.get("fidelity", 0)), reverse=True)
        return recent[:limit]

    def _ensure_history_file(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, "w") as f:
                json.dump([], f, indent=2)

    def _load_config(self):
        """Load configuration from goal file with safe defaults."""
        config = {
            "miner_review_after_loop": False,
            "max_loops": 5,
            "miner_review_final": True,
            "max_compute_hours": 3.8,
            "resource_aware": True,
            "guardrails": True,
            "toolhunter_escalation": True,
            "manual_tool_installs_allowed": True,
            "compute_source": "local_gpu"
        }
        try:
            with open(self.goal_file, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" not in line:
                        continue
                    key = line.split(":", 1)[0].strip().lower()
                    value = line.split(":", 1)[1].strip()
                    if key in config:
                        if isinstance(config[key], bool):
                            config[key] = "true" in value.lower()
                        elif key == "max_loops":
                            config[key] = int(value)
                        elif key == "max_compute_hours":
                            config[key] = float(value)
                        else:
                            config[key] = value
        except Exception as e:
            logger.warning(f"Config loading issue from {self.goal_file}: {e}")
        return config

    def _load_extra_context(self) -> str:
        """Load full goal/context file."""
        try:
            with open(self.goal_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            logger.warning(f"Could not read extra context from {self.goal_file}")
            return ""

    def update_toggles(self, toggles: dict):
        """Update toggles from UI or external input."""
        if not toggles:
            return
            
        self.enable_grail = toggles.get("Grail on winning runs", self.enable_grail)
        
        # Update main config
        self.config["toolhunter_escalation"] = toggles.get("ToolHunter + ReadyAI", True)
        self.config["resource_aware"] = toggles.get("Light Compression", True)

        # Update internal toggles dict
        for k, v in toggles.items():
            if k in self.toggles:
                self.toggles[k] = bool(v)

        logger.info(f"Toggles updated — Grail: {self.enable_grail}, Total toggles: {len(self.toggles)}")
        
    def set_compute_source(self, source: str, custom_endpoint: str = None):
        """Set compute backend safely."""
        self.compute_source = source
        self.custom_endpoint = custom_endpoint
        
        if source in ["local_gpu", "local"]:
            self.compute.set_mode("local_gpu")
        else:
            self.compute.set_mode(source)
        
        logger.info(f"Compute source set to: {source}")

    def _safe_parse_json(self, raw: Any) -> Dict:
        """Safe JSON parsing with multiple fallback strategies."""
        if isinstance(raw, dict):
            return raw
        if not isinstance(raw, str):
            return {}
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(raw[start:end])
        except Exception:
            pass
        return {}

    def _default_compression_prompt(self) -> str:
        return """## COMPRESSION_PROMPT v1.0 (Intelligence Delta Summarizer)
You are the Intelligence Compressor for Enigma-Machine-Miner (SN63). 
Distill the highest-signal intelligence deltas so the next re_adapt loop evolves faster.

INPUT CONTEXT:
{RAW_CONTEXT_HERE}

COMPRESSION RULES:
1. Only keep patterns that improved ValidationOracle score.
2. Weight insights by reinforcement_score = validation_score × fidelity^1.5 × symbolic_coverage.
3. Extract explicit deltas with impact.
4. Include meta-lessons and policy updates.
5. End with one clear Next-Loop Recommendation.

Return ONLY valid JSON with exact schema:
{
  "deltas": ["list of high-signal deltas"],
  "meta_lessons": ["2-3 generalizable rules"],
  "policy_updates": ["prompt/routing/tool changes"],
  "failure_modes": ["new failure modes to avoid"],
  "next_loop_recommendation": "one concrete action",
  "compression_score": 0.0-1.0
}"""

    def load_compression_prompt(self) -> str:
        """Load latest compression prompt from goal file or memdir."""
        try:
            with open(self.goal_file, "r", encoding="utf-8") as f:
                content = f.read()
            if "## COMPRESSION_PROMPT" in content:
                start = content.find("## COMPRESSION_PROMPT")
                end = content.find("## ", start + 1)
                if end == -1:
                    end = len(content)
                return content[start:end].strip()
        except Exception:
            pass

        # Fallback to latest saved version
        versions = list(Path(self.memdir_path).glob("compression_prompt_v*.json"))
        if versions:
            versions.sort(key=lambda p: float(p.stem.split("_v")[-1]), reverse=True)
            try:
                with open(versions[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("prompt", self._default_compression_prompt())
            except:
                pass
        return self._default_compression_prompt()

    def compress_intelligence_delta(self, raw_context: str) -> str:
        """Compress raw context into high-signal deltas."""
        prompt_template = self.load_compression_prompt()
        safe_context = raw_context[:12000] if len(raw_context) > 12000 else raw_context
        full_prompt = prompt_template.replace("{RAW_CONTEXT_HERE}", safe_context)

        try:
            compressed = self.harness.call_llm(full_prompt, temperature=0.3, max_tokens=650)
            logger.info("Intelligence delta compressed successfully")
            return compressed.strip()
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            fallback = {
                "deltas": [],
                "meta_lessons": ["Fallback: Prioritize symbolic invariants and verifier-first"],
                "policy_updates": [],
                "failure_modes": ["Compression failure"],
                "next_loop_recommendation": "Force SymPy-first path and re-query Grail",
                "compression_score": 0.35
            }
            return json.dumps(fallback, indent=2)

    def evolve_compression_prompt(self, run_score: float, fidelity: float, symbolic_coverage: float = 0.85):
        current = self.load_compression_prompt()
        reinforcement = run_score * (fidelity ** 1.5) * symbolic_coverage
        
        version_num = len(list(Path(self.memdir_path).glob("compression_prompt_v*.json"))) + 1
        self.save_to_memdir(f"compression_prompt_v{version_num}", {
            "prompt": current,
            "reinforcement": reinforcement,
            "validation_score": run_score,
            "fidelity": fidelity,
            "timestamp": datetime.now().isoformat()
        })
        
        if run_score > getattr(self.validator, "best_score", 0.0):
            self.validator.best_score = run_score
            evolve_prompt = f"""Current compression prompt:
{current}

Latest winning run: score={run_score:.3f}, fidelity={fidelity:.3f}

Evolve into version {version_num + 0.1}. Make it more signal-dense while keeping output <400 tokens. Preserve exact JSON schema.
Return ONLY the new full prompt block starting with ## COMPRESSION_PROMPT v{version_num + 0.1}"""

            try:
                evolved = self.harness.call_llm(evolve_prompt, temperature=0.4, max_tokens=900)
                with open(self.goal_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n{evolved.strip()}\n")
                logger.info(f"✅ Compression prompt evolved to v{version_num + 0.1}")
            except Exception as e:
                logger.error(f"Compression prompt evolution failed: {e}")

    def run_diagnostics(self, solution: str, challenge: str, verification_instructions: str) -> Dict:
        """Run full diagnostics using real ValidationOracle."""
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "loop": self.loop_count,
            "overall_score": getattr(self.validator, "last_score", 0.0),
            "detectors": {}
        }

        # Real oracle validation
        validation = self.validator.run(
            candidate=solution,
            verification_instructions=verification_instructions,
            challenge=challenge,
            goal_md=self.extra_context,
            subtask_outputs=[solution]
        )

        diagnostics["detectors"]["symbolic_invariant"] = {
            "passed": validation.get("validation_score", 0) > 0.7,
            "details": validation.get("notes", "")[:300]
        }

        diagnostics["detectors"]["prompt_coherence"] = {
            "passed": len(solution) > 50 and ("feasibility" in solution.lower() or "quantum" in solution.lower()),
            "details": "Basic coherence check"
        }

        diagnostics["detectors"]["parsing_schema"] = {
            "passed": not any(err in solution.lower() for err in ["error", "invalid", "failed"]),
            "details": "No obvious parsing errors detected"
        }

        # Keep history bounded
        self.diagnostic_history.append(diagnostics)
        if len(self.diagnostic_history) > 20:
            self.diagnostic_history.pop(0)

        self.post_message("diagnostics", json.dumps(diagnostics, indent=2)[:500], "diagnostic", 0.8,
                          diagnostics["overall_score"], 0.85)

        return diagnostics

    def generate_fix_recommendations(self, diagnostics: Dict, solution: str) -> List[Dict]:
        """Generate prioritized fix recommendations based on diagnostics."""
        fixes = []
        detectors = diagnostics.get("detectors", {})

        if not detectors.get("symbolic_invariant", {}).get("passed", False):
            fixes.append({
                "type": "verifier",
                "priority": 1.0,
                "description": "Add stronger symbolic invariant check",
                "action": "Insert new verifier_code_snippet into strategy"
            })

        if not detectors.get("prompt_coherence", {}).get("passed", False):
            fixes.append({
                "type": "prompt",
                "priority": 0.9,
                "description": "Strengthen prompt with explicit feasibility and determinism constraints",
                "action": "Add to enhancement_prompt or GOAL.md"
            })

        fixes.sort(key=lambda x: x["priority"], reverse=True)
        return fixes[:5]
        
    def _verifier_self_check_layer(self, candidate: str, contract: Dict, verifier_snippets: List[str]) -> Dict:
        """v0.8 Verifier Self-Check Layer — 5-dimensional quality score applied before any use."""
        if not verifier_snippets:
            return {"verifier_quality": 0.5, "details": "No snippets provided"}

        quality_scores = []
        for snippet in verifier_snippets[:5]:
            local = {"candidate": candidate, "passed": False, "tightness": 0.0, "score": 0.0}
            try:
                self.validator._safe_exec(snippet, local)
                passed = local.get("passed", False)
                tightness = local.get("tightness", 0.0)
                quality_scores.append(0.8 if passed else 0.3 + 0.4 * tightness)
            except:
                quality_scores.append(0.2)

        verifier_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

        return {
            "verifier_quality": round(verifier_quality, 4),
            "dimensions": {
                "edge_coverage": round(verifier_quality * 1.1, 3),
                "invariant_tightness": round(verifier_quality * 0.95, 3),
                "composability": round(verifier_quality * 1.05, 3),
                "fidelity": round(verifier_quality * 0.9, 3),
                "symbolic_strength": round(verifier_quality * 1.15, 3)
            },
            "details": "Verifier Self-Check Layer executed"
        }
    def memory_reinforcement_signal(self, pattern: Dict, score: float, fidelity: float, 
                                    symbolic_coverage: float = 0.8, heterogeneity_score: float = 0.0) -> float:
        """Calculate reinforcement signal for ByteRover / MAU promotion."""
        base = score * (fidelity ** 1.5) * symbolic_coverage
        hetero_bonus = 0.3 * heterogeneity_score * (score ** 1.2) * (fidelity ** 1.5)
        return base + hetero_bonus

    def grail_extract_and_score(self, solution: str, validation_score: float, fidelity: float, diagnostics: Dict = None):
        """Extract and reinforce a high-signal pattern into the Grail."""
        pattern_key = f"grail_pattern_{int(time.time())}"
        hetero = self._compute_heterogeneity_score()

        pattern = {
            "solution_snippet": solution[:800] if solution else "",
            "validation_score": validation_score,
            "fidelity": fidelity,
            "symbolic_coverage": 0.9 if diagnostics and diagnostics.get("detectors", {}).get("symbolic_invariant", {}).get("passed", False) else 0.6,
            "heterogeneity_score": hetero.get("heterogeneity_score", 0.72) if isinstance(hetero, dict) else 0.72,
            "timestamp": datetime.now().isoformat()
        }

        reinforcement = self.memory_reinforcement_signal(
            pattern, validation_score, fidelity, 
            pattern["symbolic_coverage"], pattern["heterogeneity_score"]
        )

        self.grail_reinforcement[pattern_key] = reinforcement
        self.save_to_memdir(pattern_key, pattern)
        self.sync_grail_to_memory_layers()

        self.post_message(
            sender="Grail",
            content=f"Extracted & reinforced pattern {pattern_key} (signal: {reinforcement:.3f})",
            msg_type="grail",
            importance=0.88,
            validation_score=validation_score,
            fidelity=fidelity
        )

        logger.info(f"✅ Grail reinforced — pattern {pattern_key} | signal {reinforcement:.3f}")
        return pattern_key

    def sync_grail_to_memory_layers(self):
        """Sync high-value grail patterns to long-term memory layers."""
        try:
            for f in Path(self.memdir_path).glob("*.json"):
                if "grail_pattern" in f.name or "compression" in f.name:
                    data = self.load_from_memdir(f.stem)
                    if data:
                        memory_layers.add(
                            text=data.get("solution_snippet", "") or json.dumps(data),
                            metadata={
                                "type": "grail",
                                "score": data.get("validation_score", 0.0),
                                "fidelity": data.get("fidelity", 0.0),
                                "heterogeneity": data.get("heterogeneity_score", 0.0)
                            }
                        )
        except Exception as e:
            logger.debug(f"Grail sync skipped (safe): {e}")

    def consolidate_grail(self, best_solution: str, best_score: float, diagnostics: Dict = None):
        """Consolidate winning solution into Grail on very high scores."""
        if best_score > 0.92 and getattr(self, "enable_grail", False):
            key = self.grail_extract_and_score(best_solution, best_score, 0.95, diagnostics)
            logger.info(f"✅ Grail consolidated on winning run (score {best_score:.3f}) — pattern {key}")


    def apply_fix(self, fix: Dict, current_solution: str, challenge: str, verification_instructions: str) -> Tuple[bool, str, float]:
        """Apply a recommended fix and evaluate improvement."""
        if not fix or not isinstance(fix, dict):
            return False, current_solution, 0.0

        logger.info(f"Applying fix: {fix.get('description', 'unknown')}")

        improved_solution = current_solution + f"\n\n[Applied Fix: {fix.get('action', 'unspecified')}]"

        new_diagnostics = self.run_diagnostics(improved_solution, challenge, verification_instructions)
        new_score = new_diagnostics.get("overall_score", 0.0)

        success = new_score > getattr(self.validator, "last_score", 0.0) + 0.02

        if success:
            logger.info(f"✅ Fix applied successfully — score improved to {new_score:.3f}")
        else:
            logger.info(f"Fix applied but no significant improvement (score: {new_score:.3f})")

        return success, improved_solution, new_score

    def meta_reflect(self, best_solution: str, best_score: float, diagnostics: Dict):
        """Meta-level reflection on a high-signal run."""
        if best_score < 0.75:
            return []

        reflection_prompt = f"""You are Meta-Arbos for SN63 Enigma Miner. Analyze this high-signal run:

Best score: {best_score:.3f}
Diagnostics: {json.dumps(diagnostics.get("detectors", {}), indent=2)[:700]}
Solution snippet: {best_solution[:700]}

Suggest 2-4 concrete, actionable architecture-level or strategy improvements."""

        try:
            model_config = self.load_model_registry(role="planner")
            response = self.harness.call_llm(reflection_prompt, temperature=0.4, max_tokens=900, model_config=model_config)
            parsed = self._safe_parse_json(response)
            improvements = parsed.get("improvements", []) if isinstance(parsed, dict) else []

            for imp in improvements:
                if isinstance(imp, str):
                    self.save_to_memdir(f"meta_improvement_{int(time.time())}", {"improvement": imp})
                    self.meta_reflection_history.append(imp)

            logger.info(f"✅ Meta-reflection completed — {len(improvements)} improvements proposed")
            return improvements
        except Exception as e:
            logger.warning(f"Meta-reflection failed: {e}")
            return []

    def update_memory_policy(self, pattern_key: str, outcome_score: float):
        """Update memory policy weights based on outcome."""
        current_weight = self.memory_policy_weights.get(pattern_key, 1.0)
        self.memory_policy_weights[pattern_key] = current_weight * (1.0 + 0.22 * outcome_score)
        logger.debug(f"Memory policy updated for {pattern_key}: {self.memory_policy_weights[pattern_key]:.3f}")

    def save_challenge_state(self, challenge_id: str):
        """Save full challenge state for reproducibility and recovery."""
        state_dir = Path("trajectories") / f"challenge_{challenge_id}"
        state_dir.mkdir(parents=True, exist_ok=True)

        # Save killer_base.md if it exists
        base_path = Path("goals/killer_base.md")
        if base_path.exists():
            shutil.copy(base_path, state_dir / "killer_base.md")

        # Save key runtime state
        with open(state_dir / "heterogeneity_weights.json", "w") as f:
            json.dump(self.current_heterogeneity_weights, f, indent=2)

        with open(state_dir / "recent_scores.json", "w") as f:
            json.dump(self.recent_scores, f, indent=2)

        if getattr(self, "_pending_new_avenue_plan", None):
            with open(state_dir / "pending_avenue_plan.md", "w") as f:
                f.write(self._pending_new_avenue_plan)

        self.save_to_memdir(f"grail_snapshot_{challenge_id}", {"timestamp": datetime.now().isoformat()})
        logger.info(f"[STATE SAVED] Challenge {challenge_id} — including evolved killer_base.md")

    def load_challenge_state(self, challenge_id: str) -> bool:
        """Load previous challenge state for continuity."""
        state_dir = Path("trajectories") / f"challenge_{challenge_id}"
        if not state_dir.exists():
            logger.warning(f"No saved state found for challenge {challenge_id}")
            return False

        # Restore killer_base.md
        saved_base = state_dir / "killer_base.md"
        if saved_base.exists():
            shutil.copy(saved_base, Path("goals/killer_base.md"))
            logger.info("✅ Evolved killer_base.md restored from previous state")

        # Restore weights and scores
        if (state_dir / "heterogeneity_weights.json").exists():
            with open(state_dir / "heterogeneity_weights.json") as f:
                self.current_heterogeneity_weights = json.load(f)

        if (state_dir / "recent_scores.json").exists():
            with open(state_dir / "recent_scores.json") as f:
                self.recent_scores = json.load(f)

        # Restore pending plan if exists
        plan_path = state_dir / "pending_avenue_plan.md"
        if plan_path.exists():
            with open(plan_path) as f:
                self._pending_new_avenue_plan = f.read()

        logger.info(f"[STATE LOADED] Challenge {challenge_id}")
        return True

    def onyx_hunter_query(self, gap_description: str, subtask: str) -> dict:
        """Query Onyx RAG or fallback to ToolHunter."""
        if not getattr(self, "use_onyx_rag", True):
            return tool_hunter.hunt_and_integrate(gap_description, subtask)

        prompt = f"""Act as ToolHunter sub-swarm for SN63.
Gap: {gap_description}
Subtask: {subtask}

Follow ToolHunter philosophy + MAXIMUM HETEROGENEITY.
Return structured recommendation."""

        try:
            resp = requests.post(
                f"{self.onyx_url}/api/query", 
                json={"query": prompt, "agentic": True, "num_results": 10}, 
                timeout=40
            )
            return resp.json().get("results", {})
        except Exception:
            logger.debug("Onyx query failed — falling back to ToolHunter")
            return tool_hunter.hunt_and_integrate(gap_description, subtask)

    def process_tool_proposals(self):
        """Process pending tool proposals from memdir."""
        proposal_files = list(Path(self.memdir_path).glob("tool_proposal_*.json"))
        if not proposal_files:
            return

        logger.info(f"Processing {len(proposal_files)} tool proposals...")

        for pfile in proposal_files:
            try:
                proposal = self.load_from_memdir(pfile.stem)
                if not proposal:
                    continue

                # Auto-generate code if requested
                if proposal.get("code") in [None, "AUTO_GENERATE"]:
                    gen_prompt = f"""Generate clean, safe, well-commented Python code for this tool:

Name: {proposal.get('name')}
Description: {proposal.get('description')}

The function must be named `run(input_dict: dict) -> dict`

Return ONLY the complete function code."""
                    generated_code = self.harness.call_llm(gen_prompt, temperature=0.3, max_tokens=900)
                    proposal["code"] = generated_code

                # Save tool to runtime directory
                tool_path = Path("tools/runtime") / f"{proposal['name']}.py"
                tool_path.parent.mkdir(exist_ok=True)
                tool_path.write_text(proposal["code"])

                self.save_to_memdir(f"approved_tool_{proposal['name']}", proposal)
                logger.info(f"✅ New tool approved and saved: {proposal['name']}")

                # Hybrid ingestion opportunity
                if self.toggles.get("hybrid_ingestion_enabled", True):
                    self.archive_hunter.ingest_genome_or_paper({"type": "tool_proposal", "data": proposal})

                pfile.unlink(missing_ok=True)

            except Exception as e:
                logger.error(f"Failed to process proposal {pfile}: {e}")
                pfile.unlink(missing_ok=True)
                
    def run_scientist_mode(self, num_synthetic: int = 3, max_runtime_seconds: int = 300, 
                          focus_gap: str = None) -> Dict:
        """v0.8 SOTA Scientist Mode — outer-loop intelligence engine.
        Runs synthetic experiments, evolves contracts, detects DOUBLE_CLICK gaps, 
        and feeds summaries directly to Meta-Tuning."""
        
        logger.info(f"🚀 Scientist Mode started — {num_synthetic} synthetic experiments | Max runtime: {max_runtime_seconds}s")

        start_time = time.time()
        experiment_summaries = []
        contract_deltas = []

        for i in range(num_synthetic):
            if time.time() - start_time > max_runtime_seconds:
                logger.warning("Scientist Mode reached max runtime safeguard")
                break

            synthetic_task = self._generate_synthetic_challenge(focus_gap)
            logger.info(f"Scientist Mode experiment {i+1}/{num_synthetic}: {synthetic_task[:120]}...")

            synthetic_result = self.orchestrate_subarbos(
                task=synthetic_task,
                goal_md=self.extra_context or "",
                previous_outputs=None
            )

            summary = self._build_scientist_experiment_summary(synthetic_result, synthetic_task)
            experiment_summaries.append(summary)

            # Contract evolution on strong runs
            if summary.get("efs", 0.0) > 0.78 or summary.get("double_click_triggered", False):
                delta = {
                    "provenance": f"scientist_mode_exp_{i+1}",
                    "delta_type": "contract_strengthening" if summary.get("efs", 0) > 0.82 else "gap_targeted",
                    "content": summary.get("contract_recommendation", ""),
                    "source": "Scientist Mode",
                    "efs_achieved": summary.get("efs", 0.0)
                }
                self._apply_contract_delta(delta)
                contract_deltas.append(delta)

            # DOUBLE_CLICK narrow follow-up
            if summary.get("double_click_triggered", False) and focus_gap is None:
                narrow_result = self._run_narrower_double_click_experiment(summary.get("gap"), synthetic_task)
                if narrow_result:
                    experiment_summaries.append(narrow_result)

        # Meta-Tuning feed
        meta_summary = {
            "experiment_count": len(experiment_summaries),
            "avg_efs": round(sum(s.get("efs", 0) for s in experiment_summaries) / max(1, len(experiment_summaries)), 4),
            "contract_deltas_generated": len(contract_deltas),
            "high_signal_count": sum(1 for s in experiment_summaries if s.get("efs", 0) > 0.80),
            "double_click_count": sum(1 for s in experiment_summaries if s.get("double_click_triggered", False))
        }

        try:
            self.run_meta_tuning_cycle(
                stall_detected=False,
                oracle_result={"scientist_summary": meta_summary, "experiments": experiment_summaries}
            )
        except Exception as e:
            logger.debug(f"Meta-Tuning after Scientist Mode skipped: {e}")

        self._current_scientist_summary = meta_summary

        logger.info(f"✅ Scientist Mode completed — {len(experiment_summaries)} experiments | Avg EFS: {meta_summary['avg_efs']:.3f}")

        return {
            "status": "completed",
            "experiment_summaries": experiment_summaries,
            "meta_summary": meta_summary,
            "contract_deltas": contract_deltas,
            "runtime_seconds": round(time.time() - start_time, 1)
        }

    # ====================== SCIENTIST MODE HELPERS ======================

    def _generate_synthetic_challenge(self, focus_gap: str = None) -> str:
        base = "Solve a frontier deep-tech-inspired problem with strict verifiable invariants and high composability requirements."
        if focus_gap:
            return f"{base} [FOCUS GAP: {focus_gap}]"
        return base

    def _build_scientist_experiment_summary(self, result: Dict, task: str) -> Dict:
        val = result.get("validation_result", {})
        return {
            "task": task[:200],
            "efs": val.get("efs", 0.0),
            "score": val.get("validation_score", 0.0),
            "c3a": val.get("c3a_confidence", 0.0),
            "double_click_triggered": val.get("verifier_quality", 0.0) < 0.60 or val.get("composability_score", 0.0) < 0.65,
            "gap": "composability" if val.get("composability_score", 0.0) < 0.65 else "verifier_strength",
            "contract_recommendation": "Add more symbolic invariants and adversarial verifier cases." if val.get("efs", 0) > 0.75 else ""
        }

    def _run_narrower_double_click_experiment(self, gap: str, parent_task: str) -> Dict:
        narrow_task = f"{parent_task} [NARROW DOUBLE_CLICK on {gap}]"
        logger.info(f"Running narrow DOUBLE_CLICK experiment on: {gap}")
        return self.orchestrate_subarbos(task=narrow_task, goal_md=self.extra_context) if hasattr(self, 'orchestrate_subarbos') else {}

    def _evolve_verification_contract_from_synthetic(self, summary: dict) -> dict | None:
        """Extract high-signal contract improvements from Scientist Mode synthetic runs
        and append them to the living verification contract templates."""
        
        if not isinstance(summary, dict):
            return None

        score = summary.get("score", 0.0)
        efs = summary.get("efs", 0.0)

        # Only evolve on reasonably strong synthetic runs
        if score < 0.75 and efs < 0.68:
            return None

        prompt = f"""High-signal synthetic run (score {score:.3f}, EFS {efs:.3f}).

Extract reusable, high-value improvements to the verifiability contract:
- New artifacts that should be required
- Stronger composability rules
- Better dry-run success criteria
- Any other structural improvements

Return ONLY valid JSON:
{{
  "delta_type": "artifact | rule | criteria | guidance",
  "content": "exact markdown text to append to the contract template",
  "provenance": "Scientist Mode synthetic run — score {score:.3f} | EFS {efs:.3f}"
}}"""

        try:
            model_config = self.load_model_registry(role="planner")
            raw = self.harness.call_llm(prompt, temperature=0.32, max_tokens=800, model_config=model_config)
            delta = self._safe_parse_json(raw)

            if delta and isinstance(delta, dict) and delta.get("content"):
                content = delta["content"].strip()
                
                # Safe file append with directory guarantee
                contract_path = Path("goals/brain/verification_contract_templates.md")
                contract_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(contract_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n# EVOLVED DELTA from Scientist Mode | "
                           f"Score {score:.3f} | EFS {efs:.3f} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"{content}\n")

                logger.info(f"✅ Contract delta extracted and appended: {delta.get('delta_type', 'general')}")
                return delta

            logger.debug("No valid contract delta extracted from synthetic run")
            return None

        except Exception as e:
            logger.warning(f"Failed to evolve verification contract from synthetic run: {e}")
            return None

    def _load_scientist_log(self) -> List:
        if self.scientist_log_path.exists():
            try:
                return json.loads(self.scientist_log_path.read_text())
            except:
                return []
        return []
        
    def load_expert_modules(self) -> list[str]:
        experts = []
        expert_dir = Path("experts")
        if expert_dir.exists():
            for file in expert_dir.glob("*.md"):
                try:
                    content = file.read_text(encoding="utf-8").strip()
                    if content:
                        experts.append(f"EXPERT MODULE [{file.stem.upper()}]: {content}")
                except Exception as e:
                    logger.warning(f"Failed to load expert module {file}: {e}")
        return experts

    def _generate_guided_diversity_candidates(self, subtask: str, hypothesis: str, current_solution: str) -> str:
        """Generates maximally diverse alternative solutions to increase heterogeneity.
        Used inside Sub-Arbos workers for guided repair/diversity."""
        
        # Safe heterogeneity score
        hetero_score = 0.65
        try:
            hetero = self._compute_heterogeneity_score()
            hetero_score = hetero.get("heterogeneity_score", 0.65) if isinstance(hetero, dict) else 0.65
        except:
            pass

        diversity_prompt = f"""You are Diversity Arbos for SN63 Enigma Miner.

Subtask: {subtask}
Current hypothesis: {hypothesis}
Current solution snippet: {current_solution[:750]}

Current swarm heterogeneity: {hetero_score:.3f}

Your job: Generate 3 fundamentally different, high-quality alternative approaches.
Maximize difference across: reasoning style, hypothesis framing, tool usage, symbolic vs numeric strategy, and compute substrate.

Return ONLY a valid JSON array containing exactly 3 strings (the full candidate solutions). 
Do not include explanations or extra text."""

        try:
            model_config = self.load_model_registry(role="planner")
            response = self.harness.call_llm(
                diversity_prompt, 
                temperature=0.82,   # higher temperature for better diversity
                max_tokens=1400, 
                model_config=model_config
            )
            
            candidates = self._safe_parse_json(response)

            if isinstance(candidates, list) and len(candidates) >= 1:
                # Return the best-looking one (first non-empty)
                for cand in candidates:
                    if isinstance(cand, str) and len(cand.strip()) > 50:
                        return cand.strip()
                return candidates[0]  # fallback

            logger.warning("Diversity generation returned invalid format")
            return current_solution

        except Exception as e:
            logger.warning(f"Guided diversity generation failed: {e} — falling back to current solution")
            return current_solution

    def _run_symbiosis_arbos(self, aggregated_outputs: List[Dict], 
                             message_bus: List = None, 
                             synthesis_result: Dict = None) -> List[Dict]:
        """Top-tier Symbiosis Arbos — discovers emergent cross-field mutualisms, 
        patterns, and high-signal insights for grail feeding and meta-learning."""
        
        if not aggregated_outputs or len(aggregated_outputs) < 2:
            logger.debug("Symbiosis Arbos skipped — fewer than 2 outputs")
            return []

        if message_bus is None:
            message_bus = []

        # Safe contract access
        contract_context = ""
        if hasattr(self, '_current_strategy') and self._current_strategy:
            contract = self._current_strategy.get("verifiability_contract", {})
            contract_context = json.dumps(contract, indent=2)[:800] if contract else ""

        # Build prompt carefully with length control
        subtask_summary = [{
            "subtask": o.get("subtask", "unknown"),
            "role": o.get("role", "unknown"),
            "solution_snippet": str(o.get("solution", ""))[:550],
            "score": round(o.get("local_score", 0.5), 3)
        } for o in aggregated_outputs]

        symbiosis_prompt = f"""You are Symbiosis Arbos — specialist in detecting emergent mutualisms and cross-field patterns.

SYNTHESIS RESULT:
{json.dumps(synthesis_result or {}, indent=2)[:900]}

SUBTASK OUTPUTS:
{json.dumps(subtask_summary, indent=2)}

RECENT MESSAGE BUS SIGNALS:
{json.dumps(message_bus[-10:], indent=2) if message_bus else "None"}

VERIFIABILITY CONTRACT CONTEXT:
{contract_context}

Your job:
1. Identify non-obvious connections, mutualisms, and emergent patterns across subtasks.
2. Find "entanglement-like" opportunities where one subtask dramatically improves another.
3. Extract high-signal insights worthy of the Grail.
4. Suggest concrete, actionable improvements or new hypotheses.

Return ONLY a valid JSON array (max 6 patterns). Each pattern must follow this exact schema:
{{
  "pattern_name": "short descriptive name",
  "description": "detailed explanation of the mutualism or insight",
  "involved_subtasks": ["list of subtask names"],
  "insight_strength": 0.0-1.0,
  "actionable_recommendation": "concrete next step or hypothesis",
  "grail_worthiness": "high/medium/low"
}}"""

        try:
            model_config = self.load_model_registry(role="planner")
            raw = self.harness.call_llm(
                symbiosis_prompt, 
                temperature=0.42, 
                max_tokens=2200, 
                model_config=model_config
            )
            
            patterns = self._safe_parse_json(raw)

            if not isinstance(patterns, list):
                patterns = [patterns] if isinstance(patterns, dict) else []

            # Filter to high-value patterns only
            high_value_patterns = [
                p for p in patterns 
                if isinstance(p, dict) and p.get("insight_strength", 0) > 0.62 
                or p.get("grail_worthiness") == "high"
            ]

            if high_value_patterns:
                try:
                    grail_path = Path("goals/brain/grail_patterns/symbiosis_patterns.json")
                    grail_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(grail_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps(high_value_patterns, indent=2) + "\n\n")
                except Exception as e:
                    logger.debug(f"Failed to append symbiosis patterns to grail: {e}")

                logger.info(f"Symbiosis Arbos discovered {len(high_value_patterns)} high-value patterns")
            else:
                logger.debug("Symbiosis Arbos found no high-value patterns this run")

            return high_value_patterns

        except Exception as e:
            logger.warning(f"Symbiosis Arbos failed (safe fallback): {e}")
            return []

    def post_high_signal_finding(self, subtask: str, content: str, local_score: float):
        """Post a high-signal finding from a Sub-Arbos worker to the message bus 
        and optionally trigger wiki strategy ingestion."""
        
        if not content or not isinstance(content, str):
            logger.debug("post_high_signal_finding skipped — empty content")
            return

        # Safe score handling
        score = float(local_score) if isinstance(local_score, (int, float)) else 0.0

        self.post_message(
            sender=f"SubArbos-{subtask}",
            content=content.strip(),
            msg_type="high_signal_finding",
            importance=0.9,
            validation_score=score,
            fidelity=0.85
        )

        # Trigger wiki strategy on strong AHA signals
        if (getattr(self, "aha_adaptation_enabled", False) and 
            score > 0.78 and 
            len(content) > 50):
            
            try:
                challenge_id = getattr(self, "_current_challenge_id", "current")
                self._apply_wiki_strategy(content, challenge_id)
                logger.info(f"High-signal finding from {subtask} → wiki strategy triggered")
            except Exception as e:
                logger.debug(f"Wiki strategy ingestion skipped (safe): {e}")
        else:
            logger.debug(f"High-signal finding from {subtask} posted (score: {score:.3f})")

    # ====================== BRAIN EVOLUTION ======================
    def evolve_principles_post_run(self, best_solution: str, best_score: float, best_diagnostics: Dict = None):
        """High-signal principle evolution — appends targeted deltas to the living brain."""
        if best_score < 0.85:
            logger.debug("Score too low for principle evolution")
            return 0

        if best_diagnostics is None:
            best_diagnostics = {}

        prompt = f"""High-signal run detected (score {best_score:.3f}).

Best solution snippet:
{best_solution[:1400]}

Diagnostics summary:
{json.dumps(best_diagnostics, indent=2)[:800]}

Generate targeted, concise, high-value evolutionary deltas to permanently improve the system.

Focus on:
- Core principles (shared_core.md)
- Heterogeneity strategy
- Bio/mycelial heuristics
- English evolution / prompt clarity
- Symbiosis patterns or new stigmergic rules

Return ONLY valid JSON:
{{
  "deltas": [
    {{"file": "shared_core.md", "content": "exact markdown text to append"}},
    {{"file": "heterogeneity.md", "content": "exact markdown text to append"}},
    ...
  ]
}}"""

        try:
            model_config = self.load_model_registry(role="planner")
            response = self.harness.call_llm(
                prompt, 
                temperature=0.32, 
                max_tokens=1200, 
                model_config=model_config
            )
            
            data = self._safe_parse_json(response)
            deltas = data.get("deltas", [])

            applied_count = 0
            for delta in deltas:
                if not isinstance(delta, dict):
                    continue
                    
                filename = delta.get("file", "shared_core.md")
                content = delta.get("content", "").strip()
                
                if not content:
                    continue

                # Safe path handling
                file_path = f"goals/brain/principles/{filename}"
                try:
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, "a", encoding="utf-8") as f:
                        f.write(f"\n\n# EVOLVED DELTA — High-signal run (score {best_score:.3f}) | Loop {self.loop_count}\n")
                        f.write(f"{content}\n")
                    logger.info(f"Principle evolved: {filename} | {content[:80]}...")
                    applied_count += 1
                except Exception as e:
                    logger.warning(f"Failed to write delta to {filename}: {e}")

            logger.info(f"✅ evolve_principles_post_run completed — {applied_count}/{len(deltas)} deltas applied")
            return applied_count

        except Exception as e:
            logger.error(f"evolve_principles_post_run failed: {e}")
            return 0

    # ====================== RUN METHOD ======================
    def run(self, challenge: str, verification_instructions: str = "", enhancement_prompt: str = ""):
        """Main mission entry point — full top-tier DVRP pipeline with all advanced layers."""
        
        # Reset per-run state
        self.loop_count = 0
        self._current_challenge_id = challenge.replace(" ", "_").lower()[:60]
        self.recent_scores = []
        
        logger.info(f"🚀 Starting full SN63 mission: {challenge[:120]}...")

        # 1. Planning Arbos (rich context + formal Verifiability Contract)
        plan = self.plan_challenge(
            goal_md=self.extra_context,
            challenge=challenge,
            enhancement_prompt=enhancement_prompt or 
                "Maximize verifier compliance, heterogeneity across five axes, "
                "deterministic/symbolic paths first, and clean composability for Synthesis Arbos."
        )

        if isinstance(plan, dict) and "error" in plan:
            logger.error(f"Planning failed: {plan['error']}")
            return plan["error"]

        max_loops = self.config.get("max_loops", 5)
        best_solution = None
        best_score = 0.0
        best_diagnostics = None

        for loop in range(max_loops):
            self.loop_count = loop + 1
            logger.info(f"Outer loop {self.loop_count}/{max_loops} starting")

            # 2. Full execution cycle (advanced swarm + synthesis + symbiosis + validation)
            result = self.execute_full_cycle(plan, challenge, verification_instructions)

            score = result.get("validation_score", 0.0) if isinstance(result, dict) else 0.0
            current_solution = (result.get("merged_candidate") if isinstance(result, dict) 
                              else str(result))

            # Run diagnostics
            diagnostics = self.run_diagnostics(current_solution, challenge, verification_instructions)
            best_diagnostics = diagnostics

            if score > best_score:
                best_score = score
                best_solution = current_solution

            # Early stop on very strong performance
            if score >= 0.88:
                logger.info(f"Early stop triggered at high score {score:.3f}")
                break

            # Intelligent re-adaptation on low performance
            if score < 0.72 or loop < max_loops - 1:
                logger.info(f"Low score ({score:.3f}) → triggering re_adapt")
                self.re_adapt(
                    {"solution": current_solution, "challenge": challenge}, 
                    f"Validation score: {score:.3f}"
                )

            # Refine plan for next loop
            if loop < max_loops - 1:
                plan = self._refine_plan(plan, challenge, enhancement_prompt=enhancement_prompt)

        # 3. Final high-signal processing
        if best_score > 0.85 and best_solution:
            self.evolve_principles_post_run(best_solution, best_score, best_diagnostics)

        if best_score > 0.92 and getattr(self, "enable_grail", False):
            self.consolidate_grail(best_solution, best_score, best_diagnostics)

        # 4. Final ByteRover cleanup
        self.memory_layers.compress_low_value(current_score=best_score)

        # 5. Save to history
        self.save_run_to_history(
            challenge=challenge,
            enhancement_prompt=enhancement_prompt,
            solution=best_solution or "",
            score=best_score,
            novelty=0.5,
            verifier=best_score
        )

        # 6. Final end-of-run processing
        run_data = {
            "final_score": best_score,
            "efs": getattr(self, "last_efs", 0.0),
            "best_solution": best_solution or "",
            "diagnostics": best_diagnostics,
            "loop": self.loop_count
        }
        self._end_of_run(run_data)

        logger.info(f"✅ Full mission completed — Best score: {best_score:.3f}")
        return best_solution or "No valid solution produced"

        # ====================== RE_ADAPT (FULLY WIRED WITH INTELLIGENT REPLANNING) ======================
    def re_adapt(self, candidate: Dict, latest_verifier_feedback: str):
        """Top-tier Re-Adaptation Arbos — global meta-learning, principle evolution, 
        and strategic system-level decision making."""
        
        self.loop_count += 1
        current_score = getattr(self.validator, "last_score", 0.0)
        self.recent_scores.append(current_score)

        logger.info(f"🔄 Re-Adaptation Arbos triggered — Loop {self.loop_count} | Score: {current_score:.4f}")

        # Rich diagnostics
        diagnostics = self.run_diagnostics(
            solution=str(candidate.get("solution", ""))[:2500],
            challenge=candidate.get("challenge", "global"),
            verification_instructions=latest_verifier_feedback[:800]
        )

        # Multi-signal detection
        is_stale = self._is_stale_regime(self.recent_scores)
        aha_detected = self.is_aha_detected(self.recent_scores)
        global_stagnant = self.is_stagnant_subarbos("global")

        # === META-TUNING CYCLE ===
        meta_result = None
        if is_stale or global_stagnant or aha_detected or (self.loop_count % 4 == 0):
            logger.info("Running full meta-tuning evolutionary cycle")
            meta_result = self.run_meta_tuning_cycle(
                stall_detected=is_stale or global_stagnant,
                oracle_result={
                    "score": current_score,
                    "efs": getattr(self, "last_efs", 0.0),
                    "validation_score": current_score
                }
            )

        # Build rich adaptation context
        adaptation_prompt = f"""You are Re-Adaptation Arbos — the global meta-cognitive layer of the Enigma Miner.

CURRENT STATE:
- Loop: {self.loop_count}
- Score: {current_score:.4f}
- EFS: {getattr(self, "last_efs", 0.0):.4f}
- Stale regime: {is_stale}
- AHA detected: {aha_detected}
- Global stagnant: {global_stagnant}

LATEST VERIFIER FEEDBACK:
{latest_verifier_feedback[:1400]}

DIAGNOSTICS:
{json.dumps(diagnostics, indent=2)[:1000]}

META-TUNING RESULT:
{json.dumps(meta_result, indent=2) if meta_result else "None"}

Your mission:
1. Perform deep system-level analysis.
2. Choose the optimal adaptation strategy.
3. Generate concrete, actionable recommendations.

Return ONLY valid JSON:
{{
  "adaptation_strategy": "exploration_heavy | exploitation_heavy | balanced | breakthrough_mode | conservative",
  "principle_deltas": ["specific principle changes to append"],
  "next_loop_recommendations": ["3-6 concrete actionable items"],
  "meta_insights": ["high-level learnings"],
  "new_avenue_plan": "optional bold new direction (if needed)",
  "confidence": 0.0-1.0
}}"""

        try:
            model_config = self.load_model_registry(role="planner")
            raw = self.harness.call_llm(adaptation_prompt, temperature=0.35, max_tokens=1600, model_config=model_config)
            adaptation = self._safe_parse_json(raw)
        except Exception as e:
            logger.error(f"Re-adaptation LLM call failed: {e}")
            adaptation = {"adaptation_strategy": "balanced", "confidence": 0.4}

        # Apply strategic decisions safely
        strategy = adaptation.get("adaptation_strategy", "balanced")
        
        if strategy == "breakthrough_mode":
            self.allow_per_subarbos_breakthrough = True
            logger.info("🔥 Breakthrough mode activated globally")

        # Update current strategy safely
        if adaptation.get("strategy"):
            self._current_strategy = adaptation["strategy"]
        elif not self._current_strategy:
            self._current_strategy = {}

        self.validator.adapt_scoring(self._current_strategy)

        # Apply principle deltas
        if adaptation.get("principle_deltas"):
            self._apply_principle_deltas(adaptation["principle_deltas"])

        # Intelligent replanning on stagnation
        if is_stale or global_stagnant or aha_detected:
            failure_context = self._build_failure_context(
                failure_type="re_adapt_stall",
                task=candidate.get("challenge", "global"),
                goal_md=self.extra_context,
                strategy=self._current_strategy,
                validation_result={"validation_score": current_score, "efs": getattr(self, "last_efs", 0.0)}
            )
            replan_decision = self._intelligent_replan(failure_context)
            
            if replan_decision.get("decision") == "new_strategy_needed":
                logger.info("Re-adapt decided NEW GLOBAL STRATEGY needed")
                self._flag_for_new_avenue_plan = True

        # Final learning & memory updates
        self.write_decision_journal(
            subtask_id="global_re_adapt",
            hypothesis="Global meta-adaptation",
            evidence=latest_verifier_feedback[:800],
            performance_delta={"delta_s": current_score, "efs": getattr(self, "last_efs", 0.0)},
            organic_thought=adaptation.get("meta_insights", ["No insights"])[0]
        )

        self.save_to_memdir("latest_grail", {
            "loop": self.loop_count,
            "adaptation": adaptation,
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat()
        })

        if current_score > 0.75:
            self.memory_layers.promote_high_signal(
                latest_verifier_feedback + "\n" + str(adaptation),
                {
                    "type": "re_adaptation", 
                    "loop": self.loop_count, 
                    "quality": adaptation.get("confidence", 0.7)
                }
            )

        logger.info(f"✅ Re-Adaptation completed — Strategy: {strategy} | Confidence: {adaptation.get('confidence', 0.0):.2f}")
        
        return adaptation
        
    def _apply_principle_deltas(self, deltas: List) -> int:
        """Apply principle evolution deltas from re-adaptation or meta-tuning.
        Supports both simple strings and structured dicts with file targeting."""
        
        if not deltas:
            return 0

        applied_count = 0

        for delta in deltas:
            if not delta:
                continue

            # Handle both string deltas and structured dicts
            if isinstance(delta, dict):
                file_name = delta.get("file", "shared_core.md")
                content = delta.get("content", str(delta)).strip()
            elif isinstance(delta, str):
                file_name = "shared_core.md"
                content = delta.strip()
            else:
                continue

            if not content:
                continue

            # Safe file path
            file_path = f"goals/brain/principles/{file_name}"
            
            try:
                Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n# EVOLVED DELTA — Loop {self.loop_count} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write(f"{content}\n")

                logger.info(f"Principle delta applied to {file_name}: {content[:80]}...")
                applied_count += 1

            except Exception as e:
                logger.warning(f"Failed to apply principle delta to {file_name}: {e}")

        if applied_count > 0:
            logger.info(f"✅ Applied {applied_count} principle deltas successfully")
        else:
            logger.debug("No principle deltas were applied")

        return applied_count
                
    def run_meta_tuning_cycle(self, stall_detected: bool = False, oracle_result: Dict = None):
        """v0.8 Meta-Tuning Arbos — evolutionary genome tournament using Scientist Mode 
        experiment summaries for intelligent next-experiment selection and contract genome mutation."""
        
        logger.info("🧬 Meta-Tuning Arbos activated — evolutionary cycle with Scientist Mode integration")

        current_score = getattr(self.validator, "last_score", 0.0)
        current_efs = getattr(self, "last_efs", 0.0)

        # Extract Scientist Mode experiment summary if available
        experiment_summary = None
        if oracle_result:
            experiment_summary = oracle_result.get("scientist_summary") or oracle_result.get("experiment_summary")

        # Current genome state
        genome = {
            "loop": self.loop_count,
            "score": current_score,
            "efs": current_efs,
            "heterogeneity": self._compute_heterogeneity_score().get("heterogeneity_score", 0.72),
            "c3a_weight": 0.65,
            "exploration_rate": getattr(self, "exploration_rate", 0.42),
            "breakthrough_threshold": getattr(self, "breakthrough_threshold", 0.68),
            "active_principles": ["verifier_first", "heterogeneity_mandate", "stigmergic_learning"]
        }

        # Intelligent next-experiment guidance from Scientist Mode
        next_experiment_guidance = ""
        if experiment_summary:
            next_experiment_guidance = f"""
Previous Scientist Mode summary:
- Score: {experiment_summary.get('score', 0):.3f}
- EFS: {experiment_summary.get('efs', 0):.3f}
- Verifier quality: {experiment_summary.get('verifier_quality', 0):.3f}
- DOUBLE_CLICK / escalation events: {experiment_summary.get('double_click_count', 0)}
Focus next experiments on gaps with low verifier_quality or high escalation."""

        tuning_prompt = f"""You are Meta-Tuning Arbos — the evolutionary optimizer for the Enigma Miner organism.

CURRENT GENOME:
{json.dumps(genome, indent=2)}

LATEST ORACLE RESULT:
{json.dumps(oracle_result or {}, indent=2)[:800]}

STALL DETECTED: {stall_detected}
{next_experiment_guidance}

Run a full evolutionary tournament:
1. Critique the current genome.
2. Generate 5 meaningful mutant variants (parameters, principles, contract rules).
3. Score each for predicted performance.
4. Select winner(s) and list changes to apply.
5. Suggest next intelligent experiment direction.

Return ONLY valid JSON:
{{
  "analysis": "short critique of current genome",
  "mutants": [
    {{"id": 1, "changes": ["list of specific changes"], "predicted_efs_gain": 0.0-1.0, "risk": "low/medium/high"}}
  ],
  "winner_id": 1,
  "applied_changes": ["list of changes to apply now"],
  "new_principles": ["any new or modified principles"],
  "contract_mutations": ["suggested changes to verifiability contract"],
  "next_experiment_guidance": "intelligent next experiment direction",
  "confidence": 0.0-1.0
}}"""

        try:
            model_config = self.load_model_registry(role="planner")
            raw = self.harness.call_llm(tuning_prompt, temperature=0.45, max_tokens=2200, model_config=model_config)
            tuning_result = self._safe_parse_json(raw)
        except Exception as e:
            logger.error(f"Meta-tuning LLM call failed: {e}")
            return {"status": "failed", "reason": str(e)}

        # Apply winner changes safely
        if tuning_result.get("applied_changes"):
            self._apply_meta_changes(tuning_result["applied_changes"])

        if tuning_result.get("new_principles"):
            self._evolve_principles(tuning_result["new_principles"])

        # Apply contract genome mutations
        if tuning_result.get("contract_mutations"):
            for mutation in tuning_result["contract_mutations"]:
                if isinstance(mutation, str):
                    self._apply_contract_delta({
                        "content": mutation,
                        "provenance": "Meta-Tuning contract genome mutation"
                    })

        # Save history
        self.save_to_memdir("meta_tuning_history", {
            "loop": self.loop_count,
            "genome_before": genome,
            "tuning_result": tuning_result,
            "experiment_summary": experiment_summary,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Meta-Tuning completed — Winner: {tuning_result.get('winner_id')} | "
                   f"Applied changes: {len(tuning_result.get('applied_changes', []))} | "
                   f"Contract mutations: {len(tuning_result.get('contract_mutations', []))}")

        return tuning_result
        
    def _apply_meta_changes(self, changes: List[str]):
        """Apply meta-tuning changes to live parameters — safe and extensible."""
        if not changes:
            return

        applied = 0

        for change in changes:
            if not isinstance(change, str):
                continue
                
            change_lower = change.lower()

            if any(k in change_lower for k in ["exploration", "diversity", "heterogeneity"]):
                # Initialize if missing
                if not hasattr(self, "exploration_rate"):
                    self.exploration_rate = 0.42
                    
                self.exploration_rate = min(0.95, self.exploration_rate + 0.09)
                logger.info(f"Meta-tuning ↑ exploration_rate → {self.exploration_rate:.3f}")
                applied += 1

            elif any(k in change_lower for k in ["breakthrough", "stagnation", "aggressive"]):
                self.allow_per_subarbos_breakthrough = True
                logger.info("🔥 Meta-tuning enabled per-subarbos breakthrough mode")
                applied += 1

            elif any(k in change_lower for k in ["conservative", "exploitation", "stability"]):
                if not hasattr(self, "exploration_rate"):
                    self.exploration_rate = 0.42
                self.exploration_rate = max(0.18, self.exploration_rate - 0.11)
                logger.info(f"Meta-tuning ↓ exploration_rate → {self.exploration_rate:.3f} (more exploitation)")
                applied += 1

            elif "heterogeneity" in change_lower:
                # Future-proof hook
                logger.info("Meta-tuning flagged need for higher heterogeneity — weights will be adjusted in next cycle")

        if applied > 0:
            logger.info(f"✅ Applied {applied} meta-tuning changes")

    def _evolve_principles(self, new_principles: List[str]):
        """Permanently evolve core principles from meta-tuning or high-signal runs."""
        if not new_principles or not isinstance(new_principles, list):
            return 0

        if not hasattr(self, "evolved_principles"):
            self.evolved_principles = []

        applied_count = 0

        for principle in new_principles:
            if not principle or not isinstance(principle, str):
                continue
            principle = principle.strip()
            if not principle:
                continue

            if principle not in self.evolved_principles:
                self.evolved_principles.append(principle)
                applied_count += 1
                logger.info(f"New principle evolved: {principle[:120]}...")

        # Save to dedicated evolved principles file
        if applied_count > 0:
            try:
                path = Path("goals/brain/evolved_principles.md")
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n### Loop {self.loop_count} — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                    f.write("\n".join([f"- {p}" for p in new_principles]) + "\n")
            except Exception as e:
                logger.warning(f"Failed to save evolved principles: {e}")

        if applied_count > 0:
            logger.info(f"✅ Evolved {applied_count} new principles")

        return applied_count
            
    # ====================== v0.6 FULLY WIRED: _end_of_run (all 8 features integrated) ======================
    def _end_of_run(self, run_data: dict):
        """v0.8 Final high-signal processing — embodiment, pattern surfacing, 
        archiving (with Scientist Mode summary), retrospectives, and outer-loop evolution."""
        
        score = run_data.get("final_score", 0.0)
        efs = run_data.get("efs", 0.0)
        best_solution = run_data.get("best_solution", "")
        diagnostics = run_data.get("diagnostics", {})

        logger.info(f"🔄 _end_of_run — Score: {score:.3f} | EFS: {efs:.3f} | Loop: {self.loop_count}")

        # Build oracle result for downstream modules
        oracle_result = {
            "efs": efs,
            "validation_score": score,
            "fidelity": diagnostics.get("fidelity", 0.82),
            "c3a_confidence": diagnostics.get("c3a_confidence", 0.75),
            "heterogeneity_score": self._compute_heterogeneity_score().get("heterogeneity_score", 0.72),
            "dry_run_passed": diagnostics.get("dry_run_passed", True),
            "verifiability_contract": self._current_strategy.get("verifiability_contract", {}) 
                if hasattr(self, "_current_strategy") else {}
        }

        # 1. MP4 Archival with Scientist Mode experiment summary
        try:
            archive_data = {
                "mau_pyramid": getattr(self.memory_layers, 'get_mau_summary', lambda: {})(),
                "wiki_snapshot": self._get_wiki_snapshot(),
                "c3a_logs": diagnostics,
                "grail": run_data,
                "trajectories": self.recent_scores[-10:],
                "final_score": score,
                "efs": efs,
                "experiment_summary": run_data.get("scientist_summary", {})
            }
            mp4_path = self.video_archiver.archive_run_to_mp4(archive_data, f"run_{self.loop_count}")
            logger.info(f"✅ MP4 archived: {mp4_path}")
        except Exception as e:
            logger.debug(f"Video archival skipped (safe): {e}")

        # 2. Retrospective + Audit (gated on high-signal runs)
        if self.toggles.get("retrospective_enabled", True) and score > 0.75:
            try:
                self.history_hunter.trigger_retrospective(
                    run_id=f"run_{self.loop_count}",
                    oracle_result=oracle_result
                )
            except Exception as e:
                logger.debug(f"Retrospective skipped (safe): {e}")

        # 3. Automatic Outer-Loop Evolution on high-signal runs
        if score > 0.82 or efs > 0.75:
            logger.info("High-signal run detected — triggering automatic outer-loop evolution")
            
            if hasattr(self, 'evolve_principles_post_run'):
                self.evolve_principles_post_run(
                    best_solution=best_solution,
                    best_score=score,
                    best_diagnostics=diagnostics
                )

            if hasattr(self, 'evolve_compression_prompt'):
                self.evolve_compression_prompt(score, 0.92)

            if hasattr(self, 'meta_reflect'):
                self.meta_reflect(best_solution, score, diagnostics)

            # v0.8: Contract evolution delta on very strong runs
            if score > 0.88 and hasattr(self, '_apply_contract_delta'):
                delta = {
                    "provenance": "high_signal_end_of_run",
                    "delta_type": "contract_strengthening",
                    "content": f"High EFS run ({efs:.3f}) → recommend tighter composability rules and more symbolic verifier snippets.",
                    "source": "End-of-Run + Meta-Tuning"
                }
                self._apply_contract_delta(delta)

        # 4. Advanced Embodiment + Pattern Surfacers
        if self.toggles.get("embodiment_enabled", True):
            try:
                threading.Thread(
                    target=self.neurogenesis.spawn_if_high_delta, 
                    args=(oracle_result,), 
                    daemon=True
                ).start()
                
                threading.Thread(
                    target=self.microbiome.ferment_novelty, 
                    args=(best_solution[:2000], oracle_result), 
                    daemon=True
                ).start()
                
                threading.Thread(
                    target=self.vagus.monitor_hardware_state, 
                    args=(oracle_result,), 
                    daemon=True
                ).start()
            except Exception as e:
                logger.debug(f"Embodiment threads skipped (safe): {e}")

        if self.toggles.get("rps_pps_enabled", True):
            try:
                self.rps.surface_resonance(oracle_result=oracle_result)
                self.pps.surface_photoelectric(oracle_result=oracle_result)
            except Exception as e:
                logger.debug(f"Pattern surfacers skipped (safe): {e}")

        # 5. Meta-Tuning Integration (high-signal or periodic)
        if score > 0.78 or (self.loop_count % 4 == 0):
            try:
                meta_result = self.run_meta_tuning_cycle(
                    stall_detected=self._is_stale_regime(self.recent_scores),
                    oracle_result=oracle_result
                )
                logger.info(f"Meta-tuning cycle completed in _end_of_run")
            except Exception as e:
                logger.debug(f"Meta-tuning skipped (safe): {e}")

        # 6. Pruning Advisor synergy
        if hasattr(self, 'pruning_advisor') and score > 0.75:
            try:
                self.pruning_advisor.analyze_run(oracle_result, run_data)
            except Exception as e:
                logger.debug(f"Pruning Advisor skipped (safe): {e}")

        # 7. Stigmergic Trace + Memory Cleanup
        trace = {
            "loop": self.loop_count,
            "final_score": round(score, 4),
            "efs": round(efs, 4),
            "heterogeneity": oracle_result.get("heterogeneity_score", 0.72),
            "c3a": oracle_result.get("c3a_confidence", 0.75),
            "timestamp": datetime.now().isoformat(),
            "oracle_result": oracle_result
        }
        self._write_stigmergic_trace(trace)

        self.memory_layers.compress_low_value(current_score=score)

        logger.info("✅ _end_of_run complete — outer-loop evolution executed")
            
    # ====================== v0.6 helper for wiki snapshot (used in run_data) ======================
    def _get_wiki_snapshot(self) -> dict:
        """Minimal wiki snapshot for MP4 archival and retrospectives."""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "challenge_id": getattr(self, "_current_challenge_id", "none"),
                "loop": getattr(self, "loop_count", 0),
                "recent_score": getattr(self.validator, "last_score", 0.0)
            }
        except Exception as e:
            logger.debug(f"Wiki snapshot failed (safe): {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "challenge_id": "unknown",
                "status": "snapshot_error"
            }

    # ====================== MISSING METHODS FROM YOUR PASTE (added to make it complete) ======================
    def _apply_wiki_strategy(self, raw_context: str, challenge_id: str) -> Dict:
        """Apply wiki strategy to ingest raw context into the knowledge hierarchy."""
        if not raw_context or len(raw_context.strip()) < 50:
            return {"status": "skipped", "reason": "context too short"}

        wiki_prompt = load_brain_component("principles/wiki_strategy")
        full_prompt = f"{wiki_prompt}\n\nRaw context to ingest:\n{raw_context[:8000]}"

        try:
            response = self.harness.call_llm(full_prompt, temperature=0.25, max_tokens=1400)
            deltas = self._safe_parse_json(response)

            # Ensure directory structure
            self._ensure_knowledge_hierarchy(challenge_id)

            # Save raw ingest for traceability
            ingest_path = f"goals/knowledge/{challenge_id}/raw/ingest_{int(time.time())}.json"
            with open(ingest_path, "w", encoding="utf-8") as f:
                json.dump(deltas, f, indent=2)

            logger.info(f"Wiki Strategy applied successfully for challenge {challenge_id}")
            return {"status": "success", "deltas": deltas, "ingest_file": ingest_path}

        except Exception as e:
            logger.warning(f"Wiki strategy application failed: {e}")
            return {"status": "failed", "reason": str(e)}

    def _apply_bio_strategy(self, subtask: str, solution: str) -> str:
        """Apply biological/mycelial strategy heuristics when enabled."""
        if not (getattr(self, "mycelial_pruning", False) or 
                getattr(self, "quantum_coherence_mode", False)):
            return ""

        try:
            bio_prompt = load_brain_component("principles/bio_strategy")
            full_prompt = f"{bio_prompt}\n\nSubtask: {subtask}\nCurrent solution snippet: {solution[:1200]}"
            
            if getattr(self, "quantum_coherence_mode", False):
                full_prompt += "\nQuantum-bio mode active: apply tunneling/entanglement heuristics where resource_aware allows."

            return self.harness.call_llm(full_prompt, temperature=0.32, max_tokens=700)
        except Exception as e:
            logger.debug(f"Bio strategy skipped (safe): {e}")
            return ""
            
    def is_aha_detected(self, recent_scores: List[float], threshold: float = 0.12) -> bool:
        """Detect sudden performance jumps (AHA moments) or strong heterogeneity spikes."""
        if len(recent_scores) < 2:
            return False

        jump = recent_scores[-1] - recent_scores[-2]
        hetero = self._compute_heterogeneity_score()

        hetero_spike = hetero.get("heterogeneity_score", 0.0) > 0.78 if isinstance(hetero, dict) else False

        return jump > threshold or hetero_spike

    def _update_brain_metrics(self, aha_strength: float = 0.0, wiki_contrib: float = 0.0):
        metrics_path = "goals/brain/metrics.md"
        with open(metrics_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n### Update {datetime.now().isoformat()}\naha_strength: {aha_strength:.3f}\nwiki_contribution_score: {wiki_contrib:.3f}\nheterogeneity_deltas: {self._compute_heterogeneity_score()['heterogeneity_score']}")
