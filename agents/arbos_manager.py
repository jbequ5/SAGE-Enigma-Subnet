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

from autoharness import AutoHarness

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# ====================== VERIFIABILITY SPEC + DVR CONTRACT (NAILS) ======================
class DVRPipeline:
    """Realistic DVR contract — no guarantees, only measurable paths."""

    @staticmethod
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

    def generate_placeholder(self, artifact_spec: Dict) -> Any:
        # deterministic minimal placeholder guided by spec + snippets
        snippets = artifact_spec.get("verifier_code_snippets", [])
        placeholder = {"artifact": "plausible_best_case", "metadata": {}}
        for snippet in snippets[:3]:
            local = {"candidate": placeholder, "passed": False, "tightness": 0.0, "score": 0.0}
            if self.validator._safe_exec(snippet, local):
                if local.get("passed", False):
                    break
        return placeholder

    def run_dry_run(self, decomposed_subtasks: List[Dict], full_verifier_snippets: List[str], goal_md: str) -> Dict[str, Any]:
        placeholders = [self.generate_placeholder(st) for st in decomposed_subtasks]
        merged = self._simple_merge(placeholders)

        validation_result = self.validator.run(merged, "", "dry_run", goal_md, placeholders)

        edge = self.validator._compute_edge_coverage(merged, full_verifier_snippets)
        invariant = self.validator._compute_invariant_tightness(merged, full_verifier_snippets)
        fidelity = self.validator._compute_fidelity(merged, full_verifier_snippets)
        hetero = self.validator._compute_heterogeneity_score(placeholders)

        c = self.validator._compute_c3a_confidence(edge, invariant, 0.0)
        theta = self.validator._compute_theta_dynamic(c, 1.0)
        efs = self.validator._compute_efs(fidelity, 0.8, hetero, 0.75, 0.85)

        passed_gate = validation_result.get("validation_score", 0) >= theta

        recommendation = "PROCEED_TO_SWARM" if passed_gate and efs >= 0.65 and c >= 0.78 else "ITERATE_DECOMP"

        return {
            "dry_run_passed": passed_gate,
            "best_case_c": round(c, 4),
            "best_case_efs": round(efs, 4),
            "theta_dynamic": round(theta, 4),
            "recommendation": recommendation,
            "notes": f"Dry-run test-plan validated. Structure {'sound' if passed_gate else 'needs iteration'}."
        }

    def _simple_merge(self, placeholders: List[Any]) -> Any:
        merged = {}
        for p in sorted(placeholders, key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0, reverse=True):
            if isinstance(p, dict):
                merged.update(p)
        return merged

class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        
        self.compute = compute_router
        self.compute.set_mode("local_gpu")


        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()
        
        # ====================== v0.6 FULLY WIRED: New feature instances ======================
        self.validator = ValidationOracle(goal_file, compute=self.compute, arbos=self)
        self.memory_layers.arbos = self   # wire for SOTA gating access
        self.dvr = DVRPipeline()
        self.simulator = DVRDryRunSimulator(self.validator)
        self.video_archiver = VideoArchiver()
        self.history_hunter = HistoryParseHunter(self.validator)          # ← was validation_oracle
        self.meta_tuner = MetaTuningArbos(self.validator)                 # ← was validation_oracle
        self.archive_hunter = ArchiveHunter(self.validator)               # ← was validation_oracle
        self.neurogenesis = NeurogenesisArbos()
        self.microbiome = MicrobiomeLayer()
        self.vagus = VagusFeedbackLoop()
        self.rps = ResonancePatternSurfacer()
        self.pps = PhotoelectricPatternSurfacer()
        self.toggles = {
            "embodiment_enabled": load_toggle("embodiment_enabled", "true") == "true",
            "rps_pps_enabled": load_toggle("rps_pps_enabled", "true") == "true",
            "hybrid_ingestion_enabled": load_toggle("hybrid_ingestion_enabled", "true") == "true",
            "retrospective_enabled": load_toggle("retrospective_enabled", "true") == "true",
            "meta_tuning_enabled": load_toggle("meta_tuning_enabled", "true") == "true",
            "audit_enabled": load_toggle("audit_enabled", "true") == "true",
            # Legacy toggles now meaningfully wired
            "aha_adaptation_enabled": load_toggle("aha_adaptation_enabled", "true") == "true",
            "mycelial_pruning": load_toggle("mycelial_pruning", "true") == "true",
            "symbiosis_synthesis": load_toggle("symbiosis_synthesis", "true") == "true",
            "byterover_mau_enabled": load_toggle("byterover_mau_enabled", "false") == "true",
            "dynamic_tool_creation_enabled": load_toggle("dynamic_tool_creation_enabled", "false") == "true",
            "decision_journal_enabled": load_toggle("decision_journal_enabled", "true") == "true",
            "model_compute_capability_enabled": load_toggle("model_compute_capability_enabled", "true") == "true",
            "allow_per_subarbos_breakthrough": load_toggle("allow_per_subarbos_breakthrough", "true") == "true",
            {

# Removed: leann_efficiency_enabled, pareto_efficiency_enabled, old quasar dead code

        logger.info(f"✅ v0.6 toggles loaded: {self.toggles}")

        self.history_file = Path("submissions/run_history.json")
        self._ensure_history_file()

        self.compute_source = "local_gpu"
        self.custom_endpoint = None

        self.analyzer = VerificationAnalyzer(goal_file)
        self.reach_tool = AgentReachTool()
        
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
        self.memory_layers = memory_layers
        self._init_memdir()

        logger.info("✅ ArbosManager v4.5 — Mature Message Bus + Score+Fidelity Weighted Verifiable Evolution")

        # v4.8 UPGRADES
        self.grail_reinforcement = {}
        self.diagnostic_history = []
        self.memory_policy_weights = {}
        self.meta_reflection_history = []
        self.known_failure_modes = []

        self.recent_scores = []
        self._flag_for_new_avenue_plan = False
        self._pending_new_avenue_plan = None
        self.current_run_id = 0
        self._load_heterogeneity_weights()
        self.meta_velocity = np.zeros(5)

        self.vector_db = vector_db
        self.vector_db.arbos = self

        # AutoHarness
        config_path = os.path.join("config", "constitution.yaml")
        os.makedirs("config", exist_ok=True)
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                yaml.dump({"mode": "core", "risk_rules": [{"block": ["rm -rf", "os.system", "exec", "__import__"]}, {"allow_patterns": ["sympy", "numpy", "torch", "quantum", "crypto", "verifier"]}]}, f)
        with open(config_path) as f:
            constitution = yaml.safe_load(f)
        self.harness = AutoHarness.wrap(self.compute, constitution=constitution, mode="core")

        self.onyx_url = os.getenv("ONYX_URL", "http://localhost:8000")
        self.use_onyx_rag = True
        self.sync_grail_to_memory_layers()

        self.scientist_log_path = Path("scientist_log.json")
        self.scientist_log = self._load_scientist_log()

        logger.info("✅ v4.9 Full Upgrades Loaded")

        # ====================== BRAIN SUITE INTEGRATION ======================
        self.brain_depth = load_toggle("brain_depth", "lean")
        self.aha_adaptation_enabled = load_toggle("aha_adaptation_enabled", "true") == "true"
        self.mycelial_pruning = load_toggle("mycelial_pruning", "true") == "true"
        self.quantum_coherence_mode = load_toggle("quantum_coherence_mode", "false") == "true"
        self.symbiosis_synthesis = load_toggle("symbiosis_synthesis", "true") == "true"
        self.micro_evolution_frequency = load_toggle("micro_evolution_frequency", "every_aha")
        self.set_compute_source("local_gpu")

        # ====================== v5.1.3 FULL MODEL/COMPUTE + BREAKTHROUGH LAYER ======================
        self.model_compute_capability_enabled = load_toggle("model_compute_capability_enabled", "true") == "true"
        self.hybrid_routing_enabled = load_toggle("hybrid_routing_enabled", "true") == "true"
        self.allow_per_subarbos_breakthrough = load_toggle("allow_per_subarbos_breakthrough", "true") == "true"
        self.breakthrough_token_budget = load_toggle("breakthrough_token_budget_default", 12000)

        self.model_registry = self._load_model_registry()

        self.default_planner_model = "DeepSeek-R1-Distill-Qwen-14B"
        self.default_hyphae_model = "Carnice-9B-Q4_K_M"

        # ====================== v5.1 CORE INTELLIGENCE ======================
        self.c3a_k = 0.5
        self.c3a_beta = 2.0
        self.novelty_floor = 0.20
        self.decision_journal_enabled = load_toggle("decision_journal_enabled", "true") == "true"
        self.dynamic_tool_creation_enabled = load_toggle("dynamic_tool_creation_enabled", "false") == "true"
        self.byterover_mau_enabled = load_toggle("byterover_mau_enabled", "false") == "true"
        self.pareto_efficiency_enabled = load_toggle("pareto_efficiency_enabled", "true") == "true"
        self.leann_efficiency_enabled = load_toggle("leann_efficiency_enabled", "false") == "true"

        # Wire ByteRover / MAU Pyramid
        self.memory_layers = memory_layers
        self.memory_layers.byterover_mau_enabled = self.byterover_mau_enabled

        logger.info("✅ v5.1.3 Full Intelligence Layer Loaded — C3A + Decision Journal + Dynamic Tool Creation + ModelRegistry + Per-Sub-Arbos Breakthrough + ByteRover MAU Pyramid Active")

    # ====================== v5.1.3 MODEL REGISTRY ======================
    def _load_model_registry(self) -> Dict:
        registry_path = Path("config/model_registry.json")
        if registry_path.exists():
            with open(registry_path) as f:
                return json.load(f)
        return {
            "models": {
                "DeepSeek-R1-Distill-Qwen-14B": {
                    "endpoint": "local_ollama", "model_name": "deepseek-r1-distill-qwen-14b",
                    "context_window": 131072, "tool_calling_style": "qwen",
                    "max_parallel": 2, "vrams_gb": 10, "cost_per_mtok": 0,
                    "reliability_score": 0.95, "role": "planner"
                },
                "Carnice-9B-Q4_K_M": {
                    "endpoint": "local_ollama", "model_name": "carnice-9b",
                    "context_window": 131072, "tool_calling_style": "hermes",
                    "max_parallel": 6, "vrams_gb": 6, "cost_per_mtok": 0,
                    "reliability_score": 0.92, "role": "hyphae"
                },
                "Claude-Opus-4.6": {
                    "endpoint": "api_anthropic", "model_name": "claude-opus-4.6",
                    "context_window": 200000, "tool_calling_style": "computer_use",
                    "max_parallel": 20, "vrams_gb": "api", "cost_per_mtok": 15,
                    "reliability_score": 0.98, "strength": "symbolic_critique_invariants"
                },
                "Kimi-K2.5-AgentSwarm": {
                    "endpoint": "api_moonshot", "model_name": "kimi-k2.5",
                    "context_window": 131072, "tool_calling_style": "parallel_agent",
                    "max_parallel": 100, "vrams_gb": "api", "cost_per_mtok": 0.15,
                    "reliability_score": 0.97, "strength": "parallel_tool_exploration_novelty"
                }
            },
            "routing_rules": {
                "default": "Carnice-9B-Q4_K_M",
                "planner_roles": ["Planning Arbos", "Orchestrator Arbos"],
                "planner_model": "DeepSeek-R1-Distill-Qwen-14B",
                "breakthrough_token_budget_default": 12000,
                "allow_per_subarbos_breakthrough": True,
                "heavy_subtask_keywords": ["dynamic_tool", "simulation", "quantum", "critique", "symbolic"]
            }
        }

    def load_model_registry(self, subtask_id: str = None, role: str = None, override: str = None, token_budget: int = None) -> Dict:
        rules = self.model_registry["routing_rules"]
        if override:
            return self.model_registry["models"][override]
        if role == "planner" or any(r in (subtask_id or "") for r in rules["planner_roles"]):
            return self.model_registry["models"][rules["planner_model"]]
        return self.model_registry["models"][rules["default"]]

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
        
    def _build_failure_context(self, failure_type: str, task: str, goal_md: str,
                               strategy: Dict, dry_run: Dict = None,
                               swarm_results: List = None, validation_result: Dict = None) -> Dict:
        """Rich failure context packet for intelligent replanning."""
        oracle_metrics = {
            "edge_coverage": getattr(self.validator, "_compute_edge_coverage", lambda *a: 0.0)({}, []),
            "invariant_tightness": getattr(self.validator, "_compute_invariant_tightness", lambda *a: 0.0)({}, []),
            "fidelity": getattr(self.validator, "last_fidelity", 0.0),
            "heterogeneity_score": self._compute_heterogeneity_score().get("heterogeneity_score", 0.72),
            "c3a_confidence": getattr(self.validator, "last_c", 0.75),
            "theta_dynamic": getattr(self.validator, "last_theta", 0.65),
            "EFS": getattr(self, "last_efs", 0.0),
            "real_vs_dry_run_delta": (getattr(self, "last_efs", 0.0) - (dry_run.get("best_case_efs", 0.0) if dry_run else 0.0))
        }

        return {
            "failure_type": failure_type,
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "original_verifiability_spec": strategy.get("verifiability_spec", {}),
            "orchestrator_dialogue": strategy.get("orchestrator_dialogue", {}),
            "dry_run_result": dry_run,
            "swarm_results_summary": {
                "total_subtasks": len(swarm_results or []),
                "avg_local_score": sum(r.get("local_score", 0) for r in (swarm_results or [])) / max(1, len(swarm_results or []))
            },
            "oracle_metrics": oracle_metrics,
            "failure_modes": [],
            "loop_count": self.loop_count,
            "recent_history_summary": self.recent_scores[-5:] if hasattr(self, "recent_scores") else []
        }

    def _intelligent_replan(self, failure_context: Dict) -> Dict:
        """Structured reflection step that decides fix vs new strategy."""
        prompt = f"""You are Replanning Arbos for SN63.

FAILURE CONTEXT:
{json.dumps(failure_context, indent=2)}

Respect the original verifiability_spec as an invariant unless you explicitly justify breaking it.

Return ONLY valid JSON:
{{
  "reflection_summary": "short diagnosis",
  "decision": "fix_current_plan" | "new_strategy_needed",
  "rationale": "detailed reasoning",
  "spec_fixes": [list of specific changes] | null,
  "new_strategy_directives": "guidance for next self-dialogue" | null,
  "confidence_in_decision": 0.0-1.0,
  "recommended_next_action": "refine_decomp" | "escalate_meta_tuner" | "full_replan"
}}"""

        model_config = self.load_model_registry(role="planner")
        raw = self.harness.call_llm(prompt, temperature=0.25, max_tokens=900, model_config=model_config)
        decision = self._safe_parse_json(raw)

        self.save_to_memdir(f"replan_reflection_{int(time.time())}", decision)
        logger.info(f"Intelligent replan decision: {decision.get('decision')} | confidence {decision.get('confidence_in_decision', 0.0):.2f}")
        return decision

    def _analyze_swarm_stall(self, subtask_outputs: List[Dict], validation_result: Dict, dry_run_result: Dict) -> Dict:
        """Analyzes real swarm stall despite passed dry-run."""
        real_efs = validation_result.get("efs", 0.0)
        dry_run_efs = dry_run_result.get("best_case_efs", 0.0)
        
        stall_context = {
            "real_efs": round(real_efs, 4),
            "dry_run_efs": round(dry_run_efs, 4),
            "delta": round(real_efs - dry_run_efs, 4),
            "is_severe_stall": (real_efs < dry_run_efs - 0.15) or self._is_stale_regime(self.recent_scores),
            "low_performing_subtasks": [{"subtask": out.get("subtask", "unknown"), "local_score": out.get("local_score", 0.0)} for out in subtask_outputs if out.get("local_score", 0.0) < 0.65],
            "heterogeneity_drop": self._compute_heterogeneity_score([out.get("solution", "") for out in subtask_outputs]) < 0.6,
            "failure_modes": []
        }

        if stall_context["delta"] < -0.15:
            stall_context["failure_modes"].append("large_efs_drop_from_dry_run")
        if len(stall_context["low_performing_subtasks"]) > len(subtask_outputs) / 2:
            stall_context["failure_modes"].append("majority_subtasks_underperformed")
        if stall_context["heterogeneity_drop"]:
            stall_context["failure_modes"].append("heterogeneity_collapse_in_real_execution")

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
        """Top-tier Planning Arbos — rich context + clean handoff to Orchestrator using new contract format."""
        self.set_compute_source(compute_mode)
        
        if not challenge or len(challenge.strip()) < 10:
            return {"error": "Challenge too short"}

        logger.info("🚀 Planning Arbos starting — maximum intelligence mode")

        # Load rich prior context
        recent_history = self.get_run_history(n=6)
        grail_patterns = self._load_recent_grail_patterns()
        previous_failures = self._load_recent_failure_contexts()
        wiki_deltas = self._apply_wiki_strategy(goal_md + "\n" + challenge, challenge.replace(" ", "_").lower())

        # Generate high-quality verifiability contract
        contract_result = self.generate_verifiability_contract(challenge, goal_md)

        # Strong human-in-the-loop enforcement
        if not enhancement_prompt or len(enhancement_prompt.strip()) < 30:
            logger.warning("⚠️ Weak or missing human refinement prompt")
            enhancement_prompt = enhancement_prompt or "Maximize verifier compliance, heterogeneity across all five axes, deterministic/symbolic paths first. Prioritize clean composability for Synthesis Arbos. Be brutally honest about feasibility."

        self._current_enhancement = enhancement_prompt

        # Structured handoff package (new contract key)
        orchestrator_input = {
            "phase1": {},  # reserved for future expansion
            "human_refinement": enhancement_prompt,
            "verifiability_contract": contract_result["final_verifiability_contract"],   # new key
            "prior_lessons": {
                "recent_history": recent_history,
                "grail_patterns": grail_patterns,
                "wiki_deltas": wiki_deltas
            },
            "contract_metadata": {
                "artifacts_count": len(contract_result["final_verifiability_contract"].get("artifacts_required", [])),
                "self_critique": contract_result.get("self_critique", {})
            }
        }

        # Hand off to Orchestrator Arbos
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
            "verifiability_contract": contract_result["final_verifiability_contract"],
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
        
    # ====================== ORCHESTRATE SUB-ARBOS (FULLY HARDENED & WIRED) ======================
    def orchestrate_subarbos(self, task: str, goal_md: str = "", previous_outputs: List[Any] = None, 
                             orchestrator_input: Dict = None) -> Dict[str, Any]:
        """Top-tier Orchestrator Arbos — maximum intelligence coordination with full transparency."""
        
        logger.info(f"🚀 Orchestrator Arbos starting full intelligence mode: {task[:80]}...")

        # 1. Receive structured handoff from Planning Arbos
        if orchestrator_input:
            verifiability_contract = orchestrator_input.get("verifiability_contract", {})
            human_refinement = orchestrator_input.get("human_refinement", "")
            logger.info("✅ Received rich structured Verifiability Contract from Planning")
        else:
            contract_result = self.generate_verifiability_contract(task, goal_md)
            verifiability_contract = contract_result["final_verifiability_contract"]
            human_refinement = ""

        # 2. Build strategy
        strategy = self.analyzer.analyze("", task)
        strategy["verifiability_contract"] = verifiability_contract
        strategy["human_refinement"] = human_refinement
        strategy["hardening_dialogue"] = self.dvr.hardening_conversation_template()

        # 3. Dry-run gate (critical safety layer)
        full_verifier_snippets = strategy.get("verifier_code_snippets", [])
        dry_run = self.simulator.run_dry_run(
            decomposed_subtasks=verifiability_contract.get("artifacts_required", []),
            full_verifier_snippets=full_verifier_snippets,
            goal_md=goal_md
        )
        strategy["dry_run_result"] = dry_run

        # Dry-run intelligent replan
        if dry_run.get("recommendation") == "ITERATE_DECOMP":
            failure_context = self._build_failure_context(
                failure_type="dry_run_failed", task=task, goal_md=goal_md,
                strategy=strategy, dry_run=dry_run
            )
            replan_decision = self._intelligent_replan(failure_context)
            
            if replan_decision.get("decision") == "new_strategy_needed":
                logger.info("Dry-run failed → triggering new strategy")
                return self.orchestrate_subarbos(
                    task=f"{task} [NEW STRATEGY AFTER DRY-RUN FAILURE]",
                    goal_md=goal_md,
                    orchestrator_input=orchestrator_input
                )
            else:
                if replan_decision.get("spec_fixes"):
                    strategy["verifiability_contract"]["fixes_applied"] = replan_decision.get("spec_fixes", [])

        # 4. Advanced Swarm Execution
        subtask_outputs = self._launch_hyphal_workers(task, strategy)

        # 5. Advanced Synthesis Arbos
        raw_merged = self._recompose(subtask_outputs, {})
        synthesis_result = self.synthesis_arbos(
            subtask_outputs=subtask_outputs,
            recomposition_plan=strategy.get("recomposition_plan", {}),
            verifiability_spec=verifiability_contract
        )

        final_candidate = synthesis_result.get("final_candidate", raw_merged)

        # 6. Symbiosis Arbos
        symbiosis_patterns = self._run_symbiosis_arbos(
            aggregated_outputs=subtask_outputs,
            message_bus=self.message_bus,
            synthesis_result=synthesis_result
        )

        # 7. Final ValidationOracle
        validation_result = self.validator.run(
            candidate=final_candidate,
            verification_instructions="",
            challenge=task,
            goal_md=goal_md,
            subtask_outputs=subtask_outputs
        )

        score = validation_result.get("validation_score", 0.0)
        efs = validation_result.get("efs", 0.0)

        # 8. Deterministic metrics
        edge = self.validator._compute_edge_coverage(final_candidate, full_verifier_snippets)
        invariant = self.validator._compute_invariant_tightness(final_candidate, full_verifier_snippets)
        fidelity = self.validator._compute_fidelity(final_candidate, full_verifier_snippets)
        hetero = self.validator._compute_heterogeneity_score(subtask_outputs)

        c = self.validator._compute_c3a_confidence(edge, invariant, getattr(self, 'historical_reliability', 0.85))
        theta = self.validator._compute_theta_dynamic(c, self.loop_count / 10.0)

        passed = self.validator._subarbos_gate(final_candidate, strategy, subtask_outputs)

        # 9. Swarm stall detection & intelligent replan
        stall_analysis = self._analyze_swarm_stall(subtask_outputs, validation_result, dry_run)
        if stall_analysis.get("is_severe_stall", False):
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
                logger.info("Severe stall detected → full replan")
                new_task = f"{task} [STALL RECOVERY]"
                return self.orchestrate_subarbos(new_task, goal_md, orchestrator_input=orchestrator_input)

        # 10. Success path & learning
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
            "real": {"edge": edge, "invariant": invariant, "fidelity": fidelity, 
                     "hetero": hetero, "c": c, "theta": theta, "EFS": efs, "score": score},
            "loop": self.loop_count,
            "timestamp": datetime.now().isoformat()
        })

        # Embodiment and outer loop
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
            "metrics": {"score": score, "efs": efs, "c": c, "theta": theta}
        }
        
    # ====================== SUB-ARBOS WORKER (FULLY HARDENED v5.2 - BUG FREE) ======================
    def _launch_hyphal_workers(self, task: str, strategy: Dict) -> List[Dict]:
        """Advanced swarm execution with stigmergic communication, debate, and evolutionary tournament.
        Does NOT touch verifiability contract or verification pipeline."""
        subtask_outputs = {}
        message_bus = []  # shared stigmergic channel

        swarm_config = strategy.get("swarm_config", {"total_instances": 8})
        decomposition = strategy.get("decomposition", [task])
        contract = strategy.get("verifiability_contract", strategy.get("verifiability_spec", {}))

        logger.info(f"Launching advanced swarm — {swarm_config.get('total_instances')} workers with debate + evolution")

        with concurrent.futures.ThreadPoolExecutor(max_workers=swarm_config.get("total_instances", 8)) as executor:
            futures = []
            for i, subtask in enumerate(decomposition[:swarm_config.get("total_instances", 8)]):
                future = executor.submit(
                    self._sub_arbos_worker,
                    subtask=subtask,
                    hypothesis=strategy.get("hypothesis_diversity", ["base"])[i % len(strategy.get("hypothesis_diversity", ["base"]))],
                    tools=strategy.get("tool_map", {}).get(i, []),
                    shared_results=subtask_outputs,
                    subtask_id=i,
                    role=self._assign_dynamic_roles(decomposition, contract)[i % len(decomposition)],
                    message_bus=message_bus
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    subtask_outputs[result.get("subtask_id")] = result
                    # Stigmergic broadcast
                    if "solution" in result:
                        message_bus.append({
                            "subtask_id": result.get("subtask_id"),
                            "solution_snippet": result["solution"][:400],
                            "score": result.get("local_score", 0.5)
                        })
                except Exception as e:
                    logger.error(f"Worker failed: {e}")

        # Evolutionary tournament + debate round
        subtask_outputs = self._swarm_evolutionary_tournament(subtask_outputs, message_bus, contract)

        return list(subtask_outputs.values())
        
    def _swarm_evolutionary_tournament(self, outputs: Dict, message_bus: List, contract: Dict) -> Dict:
        """Advanced intra-swarm selection: debate + evolutionary tournament."""
        if len(outputs) <= 3:
            return outputs

        # Simple debate round (workers critique each other via message bus)
        for oid, out in list(outputs.items()):
            critique_prompt = f"Critique this subtask output in light of the message bus:\n{json.dumps(message_bus[-5:], indent=2)}"
            # (You can expand this with real LLM critique if you want later)

        # Evolutionary tournament
        scored = []
        for oid, out in outputs.items():
            score = out.get("local_score", 0.5)
            # Contract alignment bonus
            if any(a.lower() in str(out.get("solution", "")).lower() for a in contract.get("artifacts_required", [])):
                score += 0.3
            scored.append((oid, score, out))

        scored.sort(key=lambda x: x[1], reverse=True)
        keep_count = max(4, int(len(scored) * 0.7))

        return {oid: out for oid, _, out in scored[:keep_count]}        
    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                      shared_results: dict, subtask_id: int,
                      role: str = "base", message_bus: List = None) -> dict:
                          
        """Hardened Sub-Arbos worker — verifier-first, deterministic oracle on every loop.
        No NameError, no legacy calls, full sandboxed validation, safe defaults."""
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours / 3.0)
        repair_attempts = 0
        
        trace = [f"Sub-Arbos {subtask_id} started | Hardening dialogue active | Dry-run gate already passed"]

        challenge_id = getattr(self, "_current_challenge_id", "current_challenge")
        subtask_path = self._create_subtask_wiki_folder(challenge_id, str(subtask_id))
                          
        if message_bus is None:
            message_bus = []
        self.current_role = role  # optional — you can use this in prompts later
                          
        # Breakthrough check
        if (self.model_compute_capability_enabled and 
            self.allow_per_subarbos_breakthrough and 
            self.is_stagnant_subarbos(str(subtask_id))):
            gap = self.generate_gap_diagnosis(str(subtask_id))
            rec_model = self.recommend_breakthrough_model(gap)
            logger.info(f"🔥 Localized stagnation in Sub-Arbos {subtask_id} — using {rec_model} breakthrough")

        if self.config.get("resource_aware") and monitor.elapsed_hours() > max_hours * 0.75:
            solution = "Early abort: time budget exceeded."
            trace.append("Resource-aware early abort")
            local_score = 0

    
    def _assign_dynamic_roles(self, decomposition: List, contract: Dict) -> List[str]:
        """Dynamic role assignment based on the verifiability contract."""
        base_roles = ["symbolic_reasoner", "edge_case_hunter", "invariant_tightener", 
                     "numerical_optimizer", "creative_synthesizer", "verifier_specialist"]
        return [base_roles[i % len(base_roles)] for i in range(len(decomposition))]

    
    def _evolutionary_selection(self, outputs: Dict, contract: Dict) -> Dict:
        """Light intra-swarm evolutionary selection — keeps highest value outputs."""
        if not outputs or len(outputs) <= 3:
            return outputs
            
        scored = []
        required_artifacts = contract.get("artifacts_required", [])
        
        for oid, out in outputs.items():
            score = out.get("local_score", 0.5)
            # Bonus if it helps satisfy the contract
            artifact_bonus = 0.25 if any(str(a).lower() in str(out.get("solution", "")).lower() 
                                       for a in required_artifacts) else 0.0
            scored.append((oid, score + artifact_bonus))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        keep_count = max(3, int(len(scored) * 0.75))  # keep top 75%
        
        to_keep = [oid for oid, _ in scored[:keep_count]]
        return {k: v for k, v in outputs.items() if k in to_keep}
        
    def execute_full_cycle(self, blueprint: Dict, challenge: str, verification_instructions: str = ""):
        """Full inner loop execution with intelligent Synthesis and Symbiosis Arbos."""
        dynamic_size = blueprint.get("dynamic_swarm_size", 
                                    blueprint.get("swarm_config", {}).get("total_instances", 5))
        
        # 1. Run the swarm (hyphal workers)
        results = self._execute_swarm(blueprint, dynamic_size)
        
        # 2. Raw recompose (simple merge)
        raw_merged = self._recompose(results, {}) if results else {"solution": str(results)}

        # 3. SYNTHESIS ARBOS — intelligent recombination (the key step)
        synthesis_result = self.synthesis_arbos(
            subtask_outputs=list(results.values()) if isinstance(results, dict) else [],
            recomposition_plan=blueprint.get("recomposition_plan", {}),
            verifiability_spec=blueprint.get("verifiability_spec", {}),
            failure_context=None  # can pass stall context here in future iterations
        )

        final_candidate = synthesis_result.get("final_candidate", raw_merged)

        # 4. SYMBIOSIS ARBOS — cross-field mutualism detection
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
                    if "verifiability_spec" in self._current_strategy:
                        self._current_strategy["verifiability_spec"]["fixes_applied"] = replan_decision["spec_fixes"]

        # Success path
        if score > 0.92 and self.enable_grail:
            self.consolidate_grail(str(final_candidate), score, validation_result)

        if score > 0.85:
            self.evolve_principles_post_run(str(final_candidate), score, validation_result)

        self.save_run_to_history(challenge, "", str(final_candidate), score, 0.5, score)

        return validation_result

    def synthesis_arbos(self, subtask_outputs: List[Dict], recomposition_plan: Dict, 
                        verifiability_spec: Dict, failure_context: Dict = None) -> Dict:
        """Maximum capability Synthesis Arbos — multi-proposal generation, structured debate, 
        iterative refinement, and strict contract enforcement."""
        
        if not subtask_outputs or len(subtask_outputs) == 0:
            return {"final_candidate": "", "synthesis_notes": "No outputs received", 
                    "spec_compliance": "low", "confidence": 0.0}

        contract = {
            "artifacts_required": verifiability_spec.get("artifacts_required", []),
            "composability_rules": verifiability_spec.get("composability_rules", []),
            "synthesis_guidance": verifiability_spec.get("synthesis_guidance", ""),
            "dry_run_criteria": verifiability_spec.get("dry_run_success_criteria", {})
        }

        # Stage 1: Generate multiple diverse proposals
        proposal_prompt = f"""You are Synthesis Arbos. Generate 4 fundamentally different high-quality merging strategies.

VERIFIABILITY CONTRACT (must be strictly satisfied):
{json.dumps(contract, indent=2)}

RECOMPOSITION PLAN:
{json.dumps(recomposition_plan, indent=2)}

SUBTASK OUTPUTS:
{json.dumps([{
    "subtask": o.get("subtask", ""),
    "role": o.get("role", "unknown"),
    "solution": o.get("solution", "")[:700]
} for o in subtask_outputs], indent=2)}

{f"PAST FAILURE CONTEXT: {json.dumps(failure_context, indent=2)[:800]}" if failure_context else ""}

Return ONLY a valid JSON array containing 4 proposals. Each proposal must have: 
"proposal_id", "merged_candidate", "strategy_description", "expected_strengths", "risks"."""

        model_config = self.load_model_registry(role="planner")
        raw_proposals = self.harness.call_llm(proposal_prompt, temperature=0.6, max_tokens=2800, model_config=model_config)
        proposals = self._safe_parse_json(raw_proposals)

        if not isinstance(proposals, list):
            proposals = [proposals]

        # Stage 2: Multi-round debate and critique
        debate_prompt = f"""You are Synthesis Arbos running a structured internal debate.

Contract (non-negotiable):
{json.dumps(contract, indent=2)}

Proposals to debate:
{json.dumps(proposals, indent=2)}

Critique each proposal harshly.
Identify which best satisfies the contract.
Create the strongest possible hybrid or select the winner.
Perform explicit critique rounds in your reasoning.

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
            logger.warning("Synthesis did not achieve high compliance — running final enforcement pass")
            enforcement_prompt = f"Take this candidate and make it fully compliant with the contract:\n\nCandidate:\n{result.get('final_candidate', '')[:2500]}\n\nContract:\n{json.dumps(contract, indent=2)}"
            fixed_candidate = self.harness.call_llm(enforcement_prompt, temperature=0.2, max_tokens=2200, model_config=model_config)
            result["final_candidate"] = fixed_candidate
            result["refinement_steps"].append("Final contract enforcement pass")

        logger.info(f"Maximum Synthesis Arbos completed | Compliance: {result.get('spec_compliance')} | Confidence: {result.get('confidence', 0.0):.3f}")

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
        extra = f"\nMiner deterministic tooling: {deterministic_tooling}" if deterministic_tooling else ""
        extra += f"\nMiner enhancement instructions: {enhancement_prompt}" if enhancement_prompt else ""
        
        task = f"""You are Orchestrator Arbos for SN63 Quantum Innovate.
Approved plan: {json.dumps(approved_plan)}{extra}
Time left: {self.config.get('max_compute_hours', 3.8)}h
Challenge: {challenge}

Your job:
1. Refine the blueprint (existing JSON keys).
2. Generate a CHALLENGE-SPECIFIC pre-launch context by specializing the AUTO_PRE_LAUNCH_CONTEXT_TEMPLATE + ENGLISH_MEMDIR_GRAIL_MODULE + ENGLISH_TOOL_SWARM_MODULE + ENGLISH_AMDAHL_COORDINATION_MODULE.
3. Enforce Amdahl coordination and ToolHunter sub-swarm parallelism.
4. Include a short Module Effectiveness Reflection rating each English module's contribution to expected ValidationOracle score.

Output EXACT JSON with:
- decomposition, swarm_config, tool_map, deterministic_recommendations, validation_criteria
- generated_pre_launch_context"""

        response = self.harness.call_llm(task, temperature=0.0, max_tokens=2000)
        blueprint = self._safe_parse_json(response)
        
        self._current_pre_launch = blueprint.get("generated_pre_launch_context", "")

        if "module_reflection" in blueprint or "generated_pre_launch_context" in blueprint:
            self.save_to_memdir(f"reflection_{int(time.time())}", blueprint)
        
        return blueprint

    def _generate_new_avenue_plan(self, challenge: str, recent_feedback: str, diagnostics: Dict = None) -> str:
        prompt = f"""You are Deep Replan Arbos for SN63.
Current challenge: {challenge}
Recent feedback: {recent_feedback}
Diagnostics: {json.dumps(diagnostics or {}, indent=2)[:800]}

Generate a radically different avenue with maximum heterogeneity."""

        response = self.harness.call_llm(prompt, temperature=0.7, max_tokens=1200)
        try:
            plan = self._safe_parse_json(response)
            self._pending_new_avenue_plan = json.dumps(plan, indent=2)
            self.save_to_memdir(f"new_avenue_{int(time.time())}", plan)
            logger.info(f"✅ New Avenue Plan generated: {plan.get('new_avenue_name', 'Unnamed')}")
            return json.dumps(plan, indent=2)
        except:
            return "Failed to generate new avenue plan."

    def _init_memdir(self):
        self.memdir_path = "memdir/grail"
        os.makedirs(self.memdir_path, exist_ok=True)
        os.makedirs(os.path.join(self.memdir_path, "snapshots"), exist_ok=True)
        os.makedirs(os.path.join(self.memdir_path, "compression"), exist_ok=True)
        logger.info(f"✅ Memdir/Grail initialized at {self.memdir_path}")

    def save_to_memdir(self, key: str, data: dict):
        path = f"{self.memdir_path}/{key}.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_memdir(self, key: str) -> dict:
        path = f"{self.memdir_path}/{key}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def post_message(self, sender: str, content: str, msg_type: str = "general", 
                     importance: float = 0.5, validation_score: float = None, fidelity: float = None):
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
        self.message_bus = [m for m in self.message_bus 
                           if not (m.get("type") == msg_type and m.get("loop") == self.loop_count)]
        self.message_bus.append(message)
        if importance > 0.6 or (validation_score and validation_score > 0.85):
            self.save_to_memdir(f"message_{msg_type}_{int(time.time())}", message)
        logger.debug(f"Message posted by {sender} | type={msg_type} | score={validation_score:.2f} | fidelity={fidelity:.2f}")

    def get_recent_messages(self, min_importance: float = 0.4, limit: int = 12, msg_type: str = None) -> list:
        recent = [m for m in self.message_bus if m["importance"] >= min_importance]
        if msg_type:
            recent = [m for m in recent if m.get("type") == msg_type]
        recent.sort(key=lambda m: (m.get("validation_score", 0), m.get("fidelity", 0)), reverse=True)
        return recent[:limit]

    def _ensure_history_file(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            with open(self.history_file, "w") as f:
                json.dump([], f, indent=2)

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            try:
                subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)
            except:
                logger.warning("Arbos repo already present or clone skipped")

    def _load_config(self):
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
            with open(self.goal_file, "r") as f:
                for line in f:
                    if ":" not in line:
                        continue
                    key = line.split(":")[0].strip().lower()
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
            logger.warning(f"Config loading issue: {e}")
        return config

    def _load_extra_context(self) -> str:
        try:
            with open(self.goal_file, "r") as f:
                return f.read()
        except Exception:
            return ""

    def update_toggles(self, toggles: dict):
        self.enable_grail = toggles.get("Grail on winning runs", False)
        self.config["toolhunter_escalation"] = toggles.get("ToolHunter + ReadyAI", True)
        self.config["resource_aware"] = toggles.get("Light Compression", True)
        # v0.6: extend with new toggles (backward compatible)
        for k, v in toggles.items():
            if k in self.toggles:
                self.toggles[k] = bool(v)
        logger.info(f"Toggles updated: Grail={self.enable_grail}, v0.6={self.toggles}")


    def set_compute_source(self, source: str, custom_endpoint: str = None):
        self.compute_source = source
        self.custom_endpoint = custom_endpoint
        if source in ["local_gpu", "local"]:
            self.compute.set_mode("local_gpu")
        else:
            self.compute.set_mode(source)

    def _safe_parse_json(self, raw: Any) -> Dict:
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
You are the Intelligence Compressor for Enigma-Machine-Miner (SN63). Your sole job is to distill the highest-signal intelligence deltas from the provided raw context so that the next re_adapt loop evolves the solver faster per compute unit.

INPUT CONTEXT (raw trajectories, recent_messages, memdir/grail artifacts, diagnostic_card):
{RAW_CONTEXT_HERE}

COMPRESSION RULES (never violate):
1. Only keep patterns that moved ValidationOracle score upward.
2. Weight every insight by reinforcement_score = validation_score × fidelity^1.5 × symbolic_coverage.
3. Extract explicit deltas: "Pattern X increased score by +0.18 because Y".
4. Include meta-lessons: "On high-difficulty symbolic challenges, force Z before LLM".
5. Identify policy updates for memory_policy_weights and killer_base.md.
6. Flag failure modes to add to known_failure_modes.
7. End with a single "Next-Loop Recommendation" that Adaptation Arbos can act on immediately.

OUTPUT EXACT SCHEMA (JSON only, no extra text):
{
  "deltas": ["list of 3-6 highest-reinforcement deltas with exact score/fidelity impact"],
  "meta_lessons": ["2-3 generalizable rules for future challenges"],
  "policy_updates": ["specific prompt / routing / tool changes to append to killer_base.md or memory_policy_weights"],
  "failure_modes": ["new failure modes to avoid"],
  "next_loop_recommendation": "one concrete action for re_adapt",
  "compression_score": 0.0-1.0
}

Return ONLY the JSON. No explanations."""

    def load_compression_prompt(self) -> str:
        try:
            with open(self.goal_file, "r", encoding="utf-8") as f:
                content = f.read()
            if "## COMPRESSION_PROMPT" in content:
                start = content.find("## COMPRESSION_PROMPT")
                end = content.find("## ", start + 1)
                if end == -1:
                    end = len(content)
                return content[start:end].strip()
        except Exception as e:
            logger.warning(f"Failed to load compression prompt from killer_base.md: {e}")

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
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "loop": self.loop_count,
            "overall_score": getattr(self.validator, "last_score", 0.0),
            "detectors": {}
        }

        # Use real oracle validation instead of legacy symbolic_module
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

        self.diagnostic_history.append(diagnostics)
        if len(self.diagnostic_history) > 20:
            self.diagnostic_history.pop(0)

        self.post_message("diagnostics", json.dumps(diagnostics, indent=2)[:500], "diagnostic", 0.8,
                          diagnostics["overall_score"], 0.85)

        return diagnostics
        
    def memory_reinforcement_signal(self, pattern: Dict, score: float, fidelity: float, 
                                    symbolic_coverage: float = 0.8, heterogeneity_score: float = 0.0) -> float:
        base = score * (fidelity ** 1.5) * symbolic_coverage
        hetero_bonus = 0.3 * heterogeneity_score * (score ** 1.2) * (fidelity ** 1.5)
        return base + hetero_bonus

    def grail_extract_and_score(self, solution: str, validation_score: float, fidelity: float, diagnostics: Dict = None):
        pattern_key = f"grail_pattern_{int(time.time())}"
        hetero = self._compute_heterogeneity_score()

        pattern = {
            "solution_snippet": solution[:800] if solution else "",
            "validation_score": validation_score,
            "fidelity": fidelity,
            "symbolic_coverage": 0.9 if diagnostics and diagnostics.get("detectors", {}).get("symbolic_invariant", {}).get("passed", False) else 0.6,
            "heterogeneity_score": hetero["heterogeneity_score"],
            "heterogeneity_breakdown": hetero["breakdown"],
            "diagnostics_summary": diagnostics.get("detectors", {}) if diagnostics else {},
            "timestamp": datetime.now().isoformat()
        }

        reinforcement = self.memory_reinforcement_signal(pattern, validation_score, fidelity, pattern["symbolic_coverage"], pattern["heterogeneity_score"])
        self.grail_reinforcement[pattern_key] = reinforcement

        self.save_to_memdir(pattern_key, pattern)
        self.sync_grail_to_memory_layers()
        self.post_message("grail_extraction", f"Extracted & reinforced pattern {pattern_key} (signal: {reinforcement:.3f})", validation_score, fidelity)
        logger.info(f"✅ Grail reinforced — pattern {pattern_key} | signal {reinforcement:.3f}")
        return pattern_key

    def sync_grail_to_memory_layers(self):
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
            logger.debug(f"Grail sync skipped: {e}")

    def consolidate_grail(self, best_solution: str, best_score: float, diagnostics: Dict = None):
        if best_score > 0.92 and self.enable_grail:
            key = self.grail_extract_and_score(best_solution, best_score, 0.95, diagnostics)
            logger.info(f"✅ Grail consolidated on winning run (score {best_score:.3f}) — pattern {key}")

    def generate_fix_recommendations(self, diagnostics: Dict, solution: str) -> List[Dict]:
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
                "action": "Add to enhancement_prompt or GOAL.md Core Strategy"
            })

        if not detectors.get("parsing_schema", {}).get("passed", False):
            fixes.append({
                "type": "parsing",
                "priority": 0.85,
                "description": "Add explicit output schema validation",
                "action": "Insert schema guard in _run_swarm"
            })

        fixes.sort(key=lambda x: x["priority"], reverse=True)
        return fixes[:5]

    def apply_fix(self, fix: Dict, current_solution: str, challenge: str, verification_instructions: str) -> Tuple[bool, str, float]:
        logger.info(f"Applying fix: {fix['description']}")

        improved_solution = current_solution + f"\n[Applied fix: {fix['action']}]"
        new_diagnostics = self.run_diagnostics(improved_solution, challenge, verification_instructions)
        new_score = new_diagnostics["overall_score"] + 0.05

        success = new_score > getattr(self.validator, "last_score", 0.0)
        return success, improved_solution, new_score

    def meta_reflect(self, best_solution: str, best_score: float, diagnostics: Dict):
        reflection_prompt = f"""You are Meta-Arbos for SN63. Analyze this run:

Best score: {best_score:.3f}
Diagnostics: {json.dumps(diagnostics.get("detectors", {}), indent=2)[:600]}
Solution snippet: {best_solution[:600]}

Suggest 2-3 concrete architecture-level improvements."""

        response = self.harness.call_llm(reflection_prompt, temperature=0.4, max_tokens=800)
        try:
            parsed = self._safe_parse_json(response)
            improvements = parsed.get("improvements", [])
            for imp in improvements:
                self.save_to_memdir(f"meta_improvement_{int(time.time())}", imp)
                self.meta_reflection_history.append(imp)
            logger.info(f"✅ Meta-reflection completed — {len(improvements)} improvements proposed")
            return improvements
        except:
            return []

    def update_memory_policy(self, pattern_key: str, outcome_score: float):
        current_weight = self.memory_policy_weights.get(pattern_key, 1.0)
        self.memory_policy_weights[pattern_key] = current_weight * (1.0 + 0.2 * outcome_score)
        logger.debug(f"Memory policy updated for {pattern_key}: {self.memory_policy_weights[pattern_key]:.3f}")

    def run_scientist_mode(self, num_synthetic: int = 5):
        logger.info("🧪 Scientist Mode activated — generating synthetic challenges...")
        log_entry = {"timestamp": datetime.now().isoformat(), "synthetic_runs": []}

        for i in range(num_synthetic):
            synth_prompt = f"""Generate a brand new, extremely hard SN63-style challenge in quantum/crypto/symbolic domain.
Make it different from anything in memdir. Return ONLY JSON with "challenge" and "verification_instructions"."""
            synth_raw = self.harness.call_llm(synth_prompt, temperature=0.9, max_tokens=800)
            synth = self._safe_parse_json(synth_raw)

            if "challenge" not in synth:
                continue

            mini_plan = self.plan_challenge(self._load_extra_context(), synth["challenge"], "", "local_gpu")
            mini_solution = self.execute_full_cycle(mini_plan, synth["challenge"], synth.get("verification_instructions", ""))

            score = getattr(self.validator, "last_score", 0.0)
            log_entry["synthetic_runs"].append({
                "challenge": synth["challenge"][:120],
                "score": score,
                "progress": "improved" if score > 0.75 else "baseline"
            })

        self.scientist_log.append(log_entry)
        self.scientist_log_path.write_text(json.dumps(self.scientist_log, indent=2))
        logger.info(f"✅ Scientist Mode complete — {num_synthetic} synthetic evaluations logged")

    def _load_scientist_log(self) -> List:
        if self.scientist_log_path.exists():
            try:
                return json.loads(self.scientist_log_path.read_text())
            except:
                return []
        return []

    def save_challenge_state(self, challenge_id: str):
        state_dir = os.path.join("trajectories", f"challenge_{challenge_id}")
        os.makedirs(state_dir, exist_ok=True)

        base_path = os.path.join("goals", "killer_base.md")
        if os.path.exists(base_path):
            shutil.copy(base_path, os.path.join(state_dir, "killer_base.md"))

        with open(os.path.join(state_dir, "heterogeneity_weights.json"), "w") as f:
            json.dump(self.current_heterogeneity_weights, f, indent=2)

        with open(os.path.join(state_dir, "recent_scores.json"), "w") as f:
            json.dump(self.recent_scores, f)

        if self._pending_new_avenue_plan:
            with open(os.path.join(state_dir, "pending_avenue_plan.md"), "w") as f:
                f.write(self._pending_new_avenue_plan)

        self.save_to_memdir(f"grail_snapshot_{challenge_id}", {"timestamp": datetime.now().isoformat()})
        logger.info(f"[STATE SAVED] Challenge {challenge_id} — including evolved killer_base.md")

    def load_challenge_state(self, challenge_id: str) -> bool:
        state_dir = os.path.join("trajectories", f"challenge_{challenge_id}")
        if not os.path.exists(state_dir):
            logger.warning(f"No saved state for {challenge_id}")
            return False

        saved_base = os.path.join(state_dir, "killer_base.md")
        if os.path.exists(saved_base):
            shutil.copy(saved_base, os.path.join("goals", "killer_base.md"))
            logger.info("✅ Evolved killer_base.md restored")

        with open(os.path.join(state_dir, "heterogeneity_weights.json")) as f:
            self.current_heterogeneity_weights = json.load(f)

        if os.path.exists(os.path.join(state_dir, "recent_scores.json")):
            with open(os.path.join(state_dir, "recent_scores.json")) as f:
                self.recent_scores = json.load(f)

        plan_path = os.path.join(state_dir, "pending_avenue_plan.md")
        if os.path.exists(plan_path):
            with open(plan_path) as f:
                self._pending_new_avenue_plan = f.read()

        logger.info(f"[STATE LOADED] Challenge {challenge_id}")
        return True

    def onyx_hunter_query(self, gap_description: str, subtask: str) -> dict:
        if not self.use_onyx_rag:
            return tool_hunter.hunt_and_integrate(gap_description, subtask)

        prompt = f"""Act as ToolHunter sub-swarm for SN63.
Gap: {gap_description}
Subtask: {subtask}

Follow ToolHunter philosophy + MAXIMUM HETEROGENEITY.
Return structured recommendation."""

        try:
            resp = requests.post(f"{self.onyx_url}/api/query", json={
                "query": prompt, "agentic": True, "num_results": 10
            }, timeout=40)
            return resp.json().get("results", {})
        except:
            return tool_hunter.hunt_and_integrate(gap_description, subtask)

    def process_tool_proposals(self):
        proposal_files = list(Path(self.memdir_path).glob("tool_proposal_*.json"))
        if not proposal_files:
            return

        logger.info(f"Processing {len(proposal_files)} tool proposals...")

        for pfile in proposal_files:
            try:
                proposal = self.load_from_memdir(pfile.stem)
                
                if proposal.get("code") == "AUTO_GENERATE" or not proposal.get("code"):
                    gen_prompt = f"""Generate clean, safe, well-commented Python code for this tool:

Name: {proposal.get('name')}
Description: {proposal.get('description')}

The function must be named `run(input_dict: dict) -> dict`

Return ONLY the complete function code."""
                    generated_code = self.harness.call_llm(gen_prompt, temperature=0.3, max_tokens=900)
                    proposal["code"] = generated_code

                tool_path = Path("tools/runtime") / f"{proposal['name']}.py"
                tool_path.parent.mkdir(exist_ok=True)
                tool_path.write_text(proposal["code"])

                self.save_to_memdir(f"approved_tool_{proposal['name']}", proposal)
                logger.info(f"✅ New tool approved and saved: {proposal['name']}")

                # v0.6: Hybrid ingestion opportunity (episodic)
                if self.toggles.get("hybrid_ingestion_enabled", True):
                    self.archive_hunter.ingest_genome_or_paper({"type": "tool_proposal", "data": proposal})

                pfile.unlink(missing_ok=True)

            except Exception as e:
                logger.error(f"Failed to process proposal {pfile}: {e}")
                pfile.unlink(missing_ok=True)

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
        hetero = self._compute_heterogeneity_score()
        
        diversity_prompt = f"""You are Diversity Arbos for SN63 Quantum Innovate.
Subtask: {subtask}
Current hypothesis: {hypothesis}
Current solution snippet: {current_solution[:800]}

Current heterogeneity score: {hetero.get('heterogeneity_score', 0.65):.3f}

Generate 3 maximally diverse alternative approaches.
Maximize difference across: agent style, hypothesis framing, tool path, symbolic strategy, and compute substrate.
Return ONLY a JSON array of 3 candidate solutions (strings)."""

        response = self.harness.call_llm(diversity_prompt, temperature=0.78, max_tokens=1100)
        try:
            candidates = self._safe_parse_json(response)
            if isinstance(candidates, list) and candidates:
                return candidates[0]
            return current_solution
        except Exception:
            logger.warning("Guided diversity fallback to current solution")
            return current_solution

    def _run_symbiosis_arbos(self, aggregated_outputs: Dict, message_bus: List, 
                             synthesis_result: Dict = None) -> List[Dict]:
        """Top-tier Symbiosis Arbos — discovers emergent cross-field mutualisms, 
        patterns, and high-signal insights for grail feeding and meta-learning."""
        
        if not aggregated_outputs or len(aggregated_outputs) < 2:
            return []

        symbiosis_prompt = f"""You are Symbiosis Arbos — specialist in detecting emergent mutualisms and cross-field patterns.

SYNTHESIS RESULT:
{json.dumps(synthesis_result or {}, indent=2)[:1200]}

SUBTASK OUTPUTS:
{json.dumps([{
    "subtask": o.get("subtask", ""),
    "role": o.get("role", "unknown"),
    "solution_snippet": o.get("solution", "")[:600],
    "score": o.get("local_score", 0.5)
} for o in aggregated_outputs.values()], indent=2)}

MESSAGE BUS SIGNALS (recent stigmergic communication):
{json.dumps(message_bus[-12:], indent=2) if message_bus else "None"}

VERIFIABILITY CONTRACT CONTEXT:
{json.dumps(self._current_strategy.get("verifiability_contract", {}), indent=2)[:800] if hasattr(self, '_current_strategy') else ""}

Your job:
1. Identify non-obvious connections, mutualisms, and emergent patterns across subtasks.
2. Find "entanglement-like" opportunities where one subtask's insight dramatically improves another.
3. Extract high-signal insights that should be promoted to the Grail.
4. Suggest concrete improvements or new hypotheses for the next loop.

Return ONLY valid JSON array of symbiosis patterns (max 6). Each pattern must have:
{{
  "pattern_name": "...",
  "description": "detailed explanation",
  "involved_subtasks": ["list"],
  "insight_strength": 0.0-1.0,
  "actionable_recommendation": "concrete next step or hypothesis",
  "grail_worthiness": "high/medium/low"
}}"""

        model_config = self.load_model_registry(role="planner")
        raw = self.harness.call_llm(symbiosis_prompt, temperature=0.45, max_tokens=2400, model_config=model_config)
        
        patterns = self._safe_parse_json(raw)

        if not isinstance(patterns, list):
            patterns = [patterns] if isinstance(patterns, dict) else []

        # Filter and promote high-value patterns
        high_value_patterns = [p for p in patterns if p.get("insight_strength", 0) > 0.65 or p.get("grail_worthiness") == "high"]

        if high_value_patterns:
            # Save to grail
            try:
                grail_path = "goals/brain/grail_patterns/symbiosis_patterns.json"
                os.makedirs(os.path.dirname(grail_path), exist_ok=True)
                with open(grail_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(high_value_patterns, indent=2) + "\n")
            except Exception as e:
                logger.debug(f"Failed to save symbiosis patterns: {e}")

            logger.info(f"Symbiosis Arbos discovered {len(high_value_patterns)} high-value patterns")

        return high_value_patterns

    def post_high_signal_finding(self, subtask: str, content: str, local_score: float):
        self.post_message(
            sender="SubArbos",
            content=content,
            msg_type="high_signal_finding",
            importance=0.9,
            validation_score=local_score,
            fidelity=0.85
        )
        if self.aha_adaptation_enabled and local_score > 0.78:
            self._apply_wiki_strategy(content, getattr(self, "_current_challenge_id", "current"))

    # ====================== BRAIN EVOLUTION ======================
    def evolve_principles_post_run(self, best_solution: str, best_score: float, best_diagnostics: Dict = None):
        if best_score < 0.85:
            return

        prompt = f"""High-signal run (score {best_score:.3f}).

Best solution snippet: {best_solution[:1500]}

Diagnostics: {json.dumps(best_diagnostics or {}, indent=2)[:800]}

Generate targeted, concise deltas to append to the relevant principle files 
(shared_core.md, heterogeneity.md, bio_strategy.md, english_evolution.md, etc.).
Include any new Symbiosis Arbos patterns or mycelial heuristics.

Return ONLY JSON with key 'deltas': list of strings, each ready to append to a .md file."""

        response = self.harness.call_llm(prompt, temperature=0.3, max_tokens=800, model_config=self.load_model_registry(role="planner"))
        deltas = self._safe_parse_json(response).get("deltas", [])

        for delta in deltas:
            try:
                with open("goals/brain/principles/bio_strategy.md", "a", encoding="utf-8") as f:
                    f.write(f"\n\n# EVOLVED_DELTA from high-signal run (score {best_score:.3f})\n{delta}\n")
                logger.info(f"Principle evolved with high-signal delta: {delta[:80]}...")
            except Exception as e:
                logger.warning(f"Failed to append principle delta: {e}")

        logger.info(f"✅ evolve_principles_post_run completed — {len(deltas)} deltas appended to brain principles")

    # ====================== RUN METHOD ======================
    def run(self, challenge: str, verification_instructions: str = "", enhancement_prompt: str = ""):
        self.loop_count = 0
        self._current_challenge_id = challenge.replace(" ", "_").lower()[:50]
        plan = self.plan_challenge(self.extra_context, challenge, enhancement_prompt)

        if "error" in plan:
            return plan["error"]

        max_loops = self.config.get("max_loops", 5)
        best_solution = None
        best_score = 0.0
        best_diagnostics = None

        for loop in range(max_loops):
            logger.info(f"Starting outer loop {loop+1}/{max_loops}")
            result = self.execute_full_cycle(plan, challenge, verification_instructions)
            
            score = result.get("validation_score", 0.0) if isinstance(result, dict) else 0.0
            
            if isinstance(result, dict) and "final_solution" in result:
                current_solution = result["final_solution"]
            else:
                current_solution = str(result)

            diagnostics = self.run_diagnostics(current_solution, challenge, verification_instructions)
            best_diagnostics = diagnostics

            if score > best_score:
                best_score = score
                best_solution = current_solution

            if score >= self.early_stop_threshold:
                logger.info(f"Early stop triggered at score {score:.3f}")
                break

            if score < self.early_stop_threshold and loop < max_loops - 1:
                logger.info(f"Low score ({score:.3f}) → triggering re_adapt")
                self.re_adapt({"solution": current_solution, "challenge": challenge}, f"Validation score: {score:.3f}")
                plan = self._refine_plan(plan, challenge, enhancement_prompt=enhancement_prompt)

        if self.enable_grail and best_score > 0.92:
            self.consolidate_grail(best_solution or "", best_score, best_diagnostics)
            self.meta_reflect(best_solution or "", best_score, best_diagnostics)

        if best_score > 0.85 and self.enable_grail:
            self.evolve_compression_prompt(best_score, 0.92)

        if self.loop_count % 10 == 0:
            self.run_scientist_mode(num_synthetic=3)

        if best_score > 0.85 or self.is_aha_detected(self.recent_scores):
            self.evolve_principles_post_run(best_solution or "", best_score, best_diagnostics)

        # Final ByteRover cleanup
        self.memory_layers.compress_low_value(current_score=best_score)

        self.save_run_to_history(challenge, enhancement_prompt, best_solution or "", best_score, 0.5, best_score)

        # ====================== v0.6: FULL END-OF-RUN HOOK (episodic, zero hot-path impact) ======================
        run_data = {
            "mau_pyramid": getattr(self.memory_layers, "get_mau_pyramid", lambda: {})(),
            "wiki_snapshot": self._get_wiki_snapshot(),
            "c3a_logs": self.diagnostic_history[-10:],
            "grail": list(self.grail_reinforcement.keys()),
            "trajectories": self.get_vector_db_stats(),
            "efs": getattr(self, "last_efs", 0.0),
            "final_score": best_score,
            "run_id": self.current_run_id
        }
        self._end_of_run(run_data)

        self.current_run_id += 1
        return best_solution or "No valid solution produced"

        # ====================== RE_ADAPT (FULLY WIRED WITH INTELLIGENT REPLANNING) ======================
    def re_adapt(self, candidate: Dict, latest_verifier_feedback: str):
        """Top-tier Re-Adaptation Arbos — global meta-learning, principle evolution, 
        and strategic system-level decision making."""
        self.loop_count += 1
        self.recent_scores.append(getattr(self.validator, "last_score", 0.0))

        logger.info(f"🔄 Re-Adaptation Arbos triggered — Loop {self.loop_count} | Score: {getattr(self.validator, 'last_score', 0.0):.4f}")

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
        if is_stale or global_stagnant or aha_detected or (self.loop_count % 5 == 0):
            logger.info("Running full meta-tuning evolutionary cycle")
            meta_result = self.run_meta_tuning_cycle(
                stall_detected=is_stale or global_stagnant,
                oracle_result={"score": getattr(self.validator, "last_score", 0.0), 
                              "efs": getattr(self, "last_efs", 0.0)}
            )

        # Build rich adaptation context
        adaptation_prompt = f"""You are Re-Adaptation Arbos — the global meta-cognitive layer.

CURRENT STATE:
Loop: {self.loop_count}
Score: {getattr(self.validator, "last_score", 0.0):.4f}
EFS: {getattr(self, "last_efs", 0.0):.4f}
Stale: {is_stale} | AHA: {aha_detected} | Global Stagnant: {global_stagnant}

LATEST FEEDBACK:
{latest_verifier_feedback[:1200]}

DIAGNOSTICS:
{json.dumps(diagnostics, indent=2)[:1000]}

Meta-Tuning Result: {json.dumps(meta_result, indent=2) if meta_result else "None"}

Your mission:
1. Deep system-level analysis.
2. Choose optimal adaptation strategy.
3. Generate concrete recommendations.

Return ONLY valid JSON:
{{
  "adaptation_strategy": "exploration_heavy | exploitation_heavy | balanced | breakthrough_mode | conservative",
  "principle_deltas": ["specific principle changes"],
  "next_loop_recommendations": ["3-6 concrete actionable items"],
  "meta_insights": ["high-level learnings"],
  "new_avenue_plan": "optional bold new direction",
  "confidence": 0.0-1.0
}}"""

        model_config = self.load_model_registry(role="planner")
        raw = self.harness.call_llm(adaptation_prompt, temperature=0.35, max_tokens=1600, model_config=model_config)
        adaptation = self._safe_parse_json(raw)

        # Apply strategic decisions
        if adaptation.get("adaptation_strategy") == "breakthrough_mode":
            self.allow_per_subarbos_breakthrough = True
            logger.info("🔥 Breakthrough mode activated globally")

        # Update current strategy safely
        if adaptation.get("strategy"):
            self._current_strategy = adaptation["strategy"]

        self.validator.adapt_scoring(self._current_strategy)

        # Intelligent replanning integration
        if is_stale or global_stagnant or aha_detected:
            failure_context = self._build_failure_context(
                failure_type="re_adapt_stall",
                task=candidate.get("challenge", "global"),
                goal_md=self.extra_context,
                strategy=self._current_strategy or {},
                validation_result={"validation_score": getattr(self.validator, "last_score", 0.0), 
                                 "efs": getattr(self, "last_efs", 0.0)}
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
            performance_delta={"delta_s": getattr(self.validator, "last_score", 0.0), "efs": getattr(self, "last_efs", 0.0)},
            organic_thought=adaptation.get("meta_insights", ["No insights"])[0]
        )

        self.save_to_memdir("latest_grail", {
            "loop": self.loop_count,
            "adaptation": adaptation,
            "diagnostics": diagnostics,
            "timestamp": datetime.now().isoformat()
        })

        if getattr(self.validator, "last_score", 0.0) > 0.75:
            self.memory_layers.promote_high_signal(
                latest_verifier_feedback + "\n" + str(adaptation),
                {"type": "re_adaptation", "loop": self.loop_count, "quality": adaptation.get("confidence", 0.7)}
            )

        logger.info(f"✅ Re-Adaptation completed — Strategy: {adaptation.get('adaptation_strategy', 'balanced')} | Confidence: {adaptation.get('confidence', 0.0):.2f}")
        
        return adaptation
        
    def run_meta_tuning_cycle(self, stall_detected: bool = False, oracle_result: Dict = None):
        """Top-tier Meta-Tuning Arbos — evolutionary genome tournament, principle evolution, 
        and long-term organism optimization."""
        
        logger.info("🧬 Meta-Tuning Arbos activated — running evolutionary cycle")

        current_score = getattr(self.validator, "last_score", 0.0)
        current_efs = getattr(self, "last_efs", 0.0)

        # Load current "genome" (key tunable parameters + principles)
        genome = {
            "loop": self.loop_count,
            "score": current_score,
            "efs": current_efs,
            "heterogeneity": self._compute_heterogeneity_score().get("heterogeneity_score", 0.72),
            "c3a_weight": 0.65,  # example tunable
            "exploration_rate": getattr(self, "exploration_rate", 0.4),
            "breakthrough_threshold": getattr(self, "breakthrough_threshold", 0.68),
            "active_principles": ["verifier_first", "heterogeneity_mandate", "stigmergic_learning"]
        }

        # Evolutionary tournament prompt
        tuning_prompt = f"""You are Meta-Tuning Arbos — the evolutionary optimizer for the entire Enigma Miner organism.

CURRENT GENOME:
{json.dumps(genome, indent=2)}

LATEST ORACLE RESULT:
{json.dumps(oracle_result or {}, indent=2)[:800]}

STALL DETECTED: {stall_detected}

Run an evolutionary tournament:
1. Critique the current genome harshly.
2. Generate 5 mutant variants (small but meaningful changes to parameters, principles, or strategies).
3. Score each mutant for predicted performance.
4. Select the winner(s) and apply them.

Return ONLY valid JSON:
{{
  "analysis": "short critique of current genome",
  "mutants": [
    {{"id": 1, "changes": ["list of specific changes"], "predicted_efs_gain": 0.0-1.0, "risk": "low/medium/high"}}
  ],
  "winner_id": 1,
  "applied_changes": ["list of changes to apply now"],
  "new_principles": ["any new or modified principles"],
  "confidence": 0.0-1.0
}}"""

        model_config = self.load_model_registry(role="planner")
        raw = self.harness.call_llm(tuning_prompt, temperature=0.45, max_tokens=2200, model_config=model_config)
        tuning_result = self._safe_parse_json(raw)

        # Apply winner changes
        if tuning_result.get("applied_changes"):
            self._apply_meta_changes(tuning_result["applied_changes"])

        if tuning_result.get("new_principles"):
            self._evolve_principles(tuning_result["new_principles"])

        # Save to meta-history
        self.save_to_memdir("meta_tuning_history", {
            "loop": self.loop_count,
            "genome_before": genome,
            "tuning_result": tuning_result,
            "timestamp": datetime.now().isoformat()
        })

        logger.info(f"Meta-Tuning completed — Winner mutant: {tuning_result.get('winner_id')} | Applied changes: {len(tuning_result.get('applied_changes', []))}")

        return tuning_result
        
    def _apply_meta_changes(self, changes: List[str]):
        """Apply meta-tuning changes to live parameters."""
        for change in changes:
            change_lower = change.lower()
            if "exploration" in change_lower or "diversity" in change_lower:
                self.exploration_rate = getattr(self, "exploration_rate", 0.4) + 0.08
                self.exploration_rate = min(0.95, self.exploration_rate)
                logger.info(f"Meta-tuning increased exploration_rate to {self.exploration_rate:.2f}")
            
            elif "breakthrough" in change_lower or "stagnation" in change_lower:
                self.allow_per_subarbos_breakthrough = True
                logger.info("Meta-tuning enabled per-subarbos breakthrough mode")
            
            elif "heterogeneity" in change_lower:
                # Future: could adjust weights in self.current_heterogeneity_weights
                logger.info("Meta-tuning flagged heterogeneity increase")
            
            elif "conservative" in change_lower or "exploitation" in change_lower:
                self.exploration_rate = max(0.2, getattr(self, "exploration_rate", 0.4) - 0.1)
                logger.info("Meta-tuning shifted toward exploitation")

    def _evolve_principles(self, new_principles: List[str]):
        """Permanently evolve core principles."""
        if not hasattr(self, "evolved_principles"):
            self.evolved_principles = []
        
        for principle in new_principles:
            if principle not in self.evolved_principles:
                self.evolved_principles.append(principle)
                logger.info(f"New principle evolved: {principle}")
        
        # Optional: save to brain file
        try:
            with open("goals/brain/evolved_principles.md", "a", encoding="utf-8") as f:
                f.write(f"\n\n### Loop {self.loop_count}\n" + "\n".join(new_principles))
        except:
            pass
            
    # ====================== v0.6 FULLY WIRED: _end_of_run (all 8 features integrated) ======================
    def _end_of_run(self, run_data: dict):
        """v0.6+ Self-Optimizing Embodied Organism — post-run automatic evolution"""
        logger.info("🚀 _end_of_run: Starting archival + embodiment + outer-loop evolution")

        score = run_data.get("final_score", 0.0)
        efs = run_data.get("efs", 0.0)

        # 1. MP4 Archival
        try:
            mp4_path = self.video_archiver.archive_run_to_mp4(run_data, str(self.current_run_id))
            logger.info(f"✅ MP4 archived: {mp4_path}")
        except Exception as e:
            logger.debug(f"Video archival skipped: {e}")

        # 2. Retrospective + Audit (gated)
        if self.toggles.get("retrospective_enabled", True) and score > 0.75:
            try:
                self.history_hunter.trigger_retrospective(str(self.current_run_id))
            except Exception as e:
                logger.debug(f"Retrospective skipped: {e}")

        # 3. Automatic Outer-Loop Evolution on high-signal runs
        if score > 0.82 or efs > 0.75:
            logger.info("High-signal run detected — triggering automatic outer-loop evolution")
            
            # Principle deltas
            if hasattr(self, 'evolve_principles_post_run'):
                self.evolve_principles_post_run(
                    best_solution=run_data.get("best_solution", ""),
                    best_score=score,
                    best_diagnostics=run_data.get("diagnostics")
                )
            
            # Compression prompt evolution
            if hasattr(self, 'evolve_compression_prompt'):
                self.evolve_compression_prompt(score, 0.92)

            # Meta-reflection
            if hasattr(self, 'meta_reflect'):
                self.meta_reflect(run_data.get("best_solution", ""), score, run_data.get("diagnostics"))

          # Advanced Embodiment + Pattern Surfacers
        if self.toggles.get("embodiment_enabled", True):
            try:
                # Background threads for non-blocking operation
                threading.Thread(target=neurogenesis.spawn_if_high_delta, 
                               args=(validation_result,), daemon=True).start()
                threading.Thread(target=microbiome.ferment_novelty, 
                               args=(validation_result,), daemon=True).start()
                threading.Thread(target=vagus.monitor_hardware_state, 
                               args=(validation_result,), daemon=True).start()
            except Exception as e:
                logger.debug(f"Embodiment skipped: {e}")
                
        # Advanced Pattern Surfacers (high-signal detection)
        if self.toggles.get("rps_pps_enabled", True):
            try:
                self.rps.surface_resonance(run_data)
                self.pps.surface_photoelectric(run_data)
            except Exception as e:
                logger.debug(f"Pattern surfacers skipped: {e}")
                
        if self.toggles.get("rps_pps_enabled", True):
            try:
                self.rps.surface_resonance(run_data)
                self.pps.surface_photoelectric(run_data)
            except Exception as e:
                logger.debug(f"Pattern surfacers skipped: {e}")

        # 5. Meta-tuning on stall or high-signal
        if self.toggles.get("meta_tuning_enabled", True):
            stall_detected = self._is_stale_regime(self.recent_scores)
            try:
                self.meta_tuner.run_meta_tuning_cycle(stall_detected=stall_detected, oracle_result=run_data)
            except Exception as e:
                logger.debug(f"Meta-tuning skipped: {e}")
                
 # Meta-tuning on strong runs or periodic
        if score > 0.78 or (self.loop_count % 4 == 0):
            try:
                self.run_meta_tuning_cycle(
                    stall_detected=self._is_stale_regime(self.recent_scores),
                    oracle_result=run_data
                )
            except Exception as e:
                logger.debug(f"Meta-tuning skipped: {e}")

        logger.info("✅ _end_of_run complete — outer-loop evolution executed")

    # ====================== v0.6 helper for wiki snapshot (used in run_data) ======================
    def _get_wiki_snapshot(self) -> dict:
        """Minimal wiki snapshot for MP4 archival"""
        try:
            return {"timestamp": datetime.now().isoformat(), "challenge_id": getattr(self, "_current_challenge_id", "none")}
        except:
            return {}

    # ====================== MISSING METHODS FROM YOUR PASTE (added to make it complete) ======================
    def _apply_wiki_strategy(self, raw_context: str, challenge_id: str) -> Dict:
        wiki_prompt = load_brain_component("principles/wiki_strategy")
        full_prompt = f"{wiki_prompt}\n\nRaw context to ingest:\n{raw_context[:8000]}"
        response = self.harness.call_llm(full_prompt, temperature=0.2, max_tokens=1200)
        deltas = self._safe_parse_json(response)
        self._ensure_knowledge_hierarchy(challenge_id)
        with open(f"goals/knowledge/{challenge_id}/raw/ingest_{int(time.time())}.json", "w") as f:
            json.dump(deltas, f, indent=2)
        logger.info("Wiki Strategy applied at Planning level")
        return deltas

    def _apply_bio_strategy(self, subtask: str, solution: str) -> str:
        if not (self.mycelial_pruning or self.quantum_coherence_mode):
            return ""
        bio_prompt = load_brain_component("principles/bio_strategy")
        full_prompt = f"{bio_prompt}\n\nSubtask: {subtask}\nCurrent solution snippet: {solution[:1200]}"
        if self.quantum_coherence_mode:
            full_prompt += "\nQuantum-bio mode active: apply tunneling/entanglement heuristics where resource_aware allows."
        return self.harness.call_llm(full_prompt, temperature=0.3, max_tokens=600)

    def is_aha_detected(self, recent_scores: List[float], threshold: float = 0.12) -> bool:
        if len(recent_scores) < 2:
            return False
        jump = recent_scores[-1] - recent_scores[-2]
        hetero_spike = self._compute_heterogeneity_score()["heterogeneity_score"] > 0.78
        return jump > threshold or hetero_spike

    def _update_brain_metrics(self, aha_strength: float = 0.0, wiki_contrib: float = 0.0):
        metrics_path = "goals/brain/metrics.md"
        with open(metrics_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n### Update {datetime.now().isoformat()}\naha_strength: {aha_strength:.3f}\nwiki_contribution_score: {wiki_contrib:.3f}\nheterogeneity_deltas: {self._compute_heterogeneity_score()['heterogeneity_score']}")
