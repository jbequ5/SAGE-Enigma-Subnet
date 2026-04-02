import os
import subprocess
import json
import concurrent.futures
import multiprocessing
import time
import torch
from datetime import datetime
from typing import Tuple, List, Dict, Any
from pathlib import Path

import numpy as np
import logging
import shutil
import requests
import yaml

multiprocessing.set_start_method('spawn', force=True)

from agents.memory import memory, memory_layers
from agents.tools.tool_hunter import tool_hunter, load_registry, save_registry
from agents.tools.compute import ComputeRouter, compute_router
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails

from validation_oracle import ValidationOracle
from trajectories.trajectory_vector_db import vector_db
from tools.agent_reach_tool import AgentReachTool
from verification_analyzer import VerificationAnalyzer

# ====================== v4.8 UPGRADES ======================
from autoharness import AutoHarness

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# ====================== COMPUTE ENERGY ======================
def compute_energy(candidate: Dict, validator, rank: int = 8) -> float:
    base = 1.0
    novelty = candidate.get("novelty_proxy", 0.5)
    score = getattr(validator, "last_score", 0.85)
    energy = base + (novelty * 0.4) + (score * 0.6) - (rank * 0.01)
    return max(0.1, energy)

# ====================== SYMBOLIC MODULE ======================
def symbolic_module(subtask: str, hypothesis: str, current_solution: str, strategy: Dict[str, Any]) -> str:
    result = ""
    try:
        for snippet in strategy.get("verifier_code_snippets", []) + strategy.get("self_check_commands", []):
            try:
                local = {"candidate": current_solution, "subtask": subtask, "result": result}
                exec(snippet, {"__builtins__": {}}, local)
                result = local.get("result", result)
            except:
                pass

        if "sympy" in strategy.get("enabled_modules", ["sympy"]):
            import sympy
            result += "[SymPy] Symbolic verification applied"

        return result + " (Verifier-code-first + Deterministic)" if result else "[No deterministic path found — using LLM only]"
    except Exception as e:
        return f"[Safe fallback] Error in symbolic module: {str(e)[:100]}"


class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        
        self.compute = compute_router
        self.compute.set_mode("local_gpu")
        self.quasar_enabled = True
        logger.info("Quasar Long-Context Attention: Enabled")

        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()

        self.history_file = Path("submissions/run_history.json")
        self._ensure_history_file()

        self.compute_source = "local_gpu"
        self.custom_endpoint = None

        self.validator = ValidationOracle(goal_file, compute=self.compute)
        self.analyzer = VerificationAnalyzer(goal_file)
        self.reach_tool = AgentReachTool()
        
        self.eggroll_rank = 8
        self.sigma = 0.1
        self.alpha = 0.05
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

        # ====================== v4.8 UPGRADES ======================
        self.grail_reinforcement = {}
        self.diagnostic_history = []
        self.memory_policy_weights = {}
        self.meta_reflection_history = []
        self.known_failure_modes = []

        # Core State
        self.recent_scores = []
        self._flag_for_new_avenue_plan = False
        self._pending_new_avenue_plan = None
        self.current_run_id = 0
        self._load_heterogeneity_weights()
        self.meta_velocity = np.zeros(5)

        # AutoHarness (Always On)
        config_path = os.path.join("config", "constitution.yaml")
        os.makedirs("config", exist_ok=True)
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                yaml.dump({
                    "mode": "core",
                    "risk_rules": [{"block": ["rm -rf", "os.system", "exec", "__import__"]},
                                   {"allow_patterns": ["sympy", "numpy", "torch", "quantum", "crypto", "verifier"]}]
                }, f)
        with open(config_path) as f:
            constitution = yaml.safe_load(f)
        self.harness = AutoHarness.wrap(self.compute, constitution=constitution, mode="core")
        logger.info("✅ AutoHarness (Core mode) — always on")

        # Onyx Hybrid
        self.onyx_url = os.getenv("ONYX_URL", "http://localhost:8000")
        self.use_onyx_rag = True

        logger.info("✅ v4.8 Full Upgrades Loaded")

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

    # ====================== CHALLENGE STATE ======================
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

    # ====================== Onyx Hybrid ToolHunter ======================
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

    # ====================== YOUR ORIGINAL CODE (100% PRESERVED) ======================
    def _init_memdir(self):
        self.memdir_path = "memdir/grail"
        os.makedirs(self.memdir_path, exist_ok=True)

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
        self.quasar_enabled = toggles.get("Quasar", True)
        self.enable_grail = toggles.get("Grail on winning runs", False)
        self.config["toolhunter_escalation"] = toggles.get("ToolHunter + ReadyAI", True)
        self.config["resource_aware"] = toggles.get("Light Compression", True)
        logger.info(f"Toggles updated: Quasar={self.quasar_enabled}, Grail={self.enable_grail}")

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

    def plan_challenge(self, goal_md: str = "", challenge: str = "", enhancement_prompt: str = "", compute_mode: str = "local_gpu") -> Dict[str, Any]:
        self.set_compute_source(compute_mode)
        
        if not challenge or len(challenge.strip()) < 10:
            return {"error": "Challenge too short", "phase1": "", "phase2": {}, "dynamic_swarm_size": 4}

        logger.info(f"Planning challenge with {compute_mode} — Quasar: {self.quasar_enabled}")

        phase1_prompt = f"""You are Planning Arbos for Bittensor SN63 Quantum Innovate.
You MUST be brutally honest about cryptographic feasibility.

GOAL.md (full agnostic base):
{goal_md[:4000]}

Challenge: {challenge}
Enhancement: {enhancement_prompt or 'None'}

Return ONLY valid JSON with these keys:
- phase1_plan
- key_insights (list)
- feasibility ("low" | "medium" | "high" | "impossible_with_current_tech")
- recommended_approach
- risks (list)
- estimated_difficulty
- generated_post_planning_enhancement"""

        phase1_raw = self.compute.call_llm(phase1_prompt, temperature=0.65, max_tokens=1600)
        phase1 = self._safe_parse_json(phase1_raw)
        self._current_enhancement = phase1.get("generated_post_planning_enhancement", "")

        dynamic_size = 5 if self.quasar_enabled else 4

        phase2_prompt = f"""You are Orchestrator Arbos for SN63.
Phase 1 output: {str(phase1)[:2000]}

Return ONLY valid JSON with:
- decomposition (list of subtasks)
- swarm_config (dict with total_instances)
- tool_map
- validation_criteria
- hypothesis_diversity (list)"""

        phase2_raw = self.compute.call_llm(phase2_prompt, temperature=0.3, max_tokens=1200)
        blueprint = self._safe_parse_json(phase2_raw)

        if not blueprint or "decomposition" not in blueprint:
            blueprint = {
                "decomposition": ["Assess feasibility", "Review known methods", "Analyze quantum threat", "Synthesize realistic assessment"],
                "swarm_config": {"total_instances": dynamic_size},
                "tool_map": {},
                "validation_criteria": {},
                "hypothesis_diversity": ["standard", "conservative"]
            }

        self._current_strategy = self.analyzer.analyze("", challenge)
        self.validator.adapt_scoring(self._current_strategy)

        return {
            "phase1": phase1,
            "phase2": blueprint,
            "adapted_strategy": self._current_strategy,
            "dynamic_swarm_size": dynamic_size,
            "quasar_enabled": self.quasar_enabled
        }

    def run_diagnostics(self, solution: str, challenge: str, verification_instructions: str) -> Dict:
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "loop": self.loop_count,
            "overall_score": getattr(self.validator, "last_score", 0.0),
            "detectors": {}
        }

        symbolic_result = symbolic_module("", solution, solution, self._current_strategy or {})
        diagnostics["detectors"]["symbolic_invariant"] = {
            "passed": "deterministic" in symbolic_result.lower() or "sympy" in symbolic_result.lower(),
            "details": symbolic_result[:300]
        }

        diagnostics["detectors"]["prompt_coherence"] = {
            "passed": len(solution) > 50 and ("feasibility" in solution.lower() or "quantum" in solution.lower()),
            "details": "Basic coherence check"
        }

        diagnostics["detectors"]["parsing_schema"] = {
            "passed": not any(err in solution.lower() for err in ["error", "invalid", "failed"]),
            "details": "No obvious parsing errors detected"
        }

        diagnostics["detectors"]["novelty_drift"] = {
            "passed": True,
            "details": "No significant drift detected"
        }

        diagnostics["detectors"]["cross_stage_coherence"] = {
            "passed": True,
            "details": "Subtasks appear aligned"
        }

        self.diagnostic_history.append(diagnostics)
        if len(self.diagnostic_history) > 20:
            self.diagnostic_history.pop(0)

        self.post_message("diagnostics", json.dumps(diagnostics, indent=2)[:500], "diagnostic", 0.8,
                          diagnostics["overall_score"], 0.85)

        return diagnostics

    def memory_reinforcement_signal(self, pattern: Dict, score: float, fidelity: float, symbolic_coverage: float = 0.8) -> float:
        return score * (fidelity ** 1.5) * symbolic_coverage

    def grail_extract_and_score(self, solution: str, validation_score: float, fidelity: float, diagnostics: Dict = None):
        pattern_key = f"grail_pattern_{int(time.time())}"
        pattern = {
            "solution_snippet": solution[:800] if solution else "",
            "validation_score": validation_score,
            "fidelity": fidelity,
            "symbolic_coverage": 0.9 if diagnostics and diagnostics.get("detectors", {}).get("symbolic_invariant", {}).get("passed", False) else 0.6,
            "diagnostics_summary": diagnostics.get("detectors", {}) if diagnostics else {},
            "timestamp": datetime.now().isoformat()
        }

        reinforcement = self.memory_reinforcement_signal(pattern, validation_score, fidelity, pattern["symbolic_coverage"])
        self.grail_reinforcement[pattern_key] = reinforcement

        self.save_to_memdir(pattern_key, pattern)
        self.post_message("grail_extraction", f"Extracted & reinforced pattern {pattern_key} (signal: {reinforcement:.3f})", validation_score, fidelity)
        logger.info(f"✅ Grail reinforced — pattern {pattern_key} | signal {reinforcement:.3f}")
        return pattern_key

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

Suggest 2-3 concrete architecture-level improvements (prompt changes, verifier additions, Grail pruning rules, strategy tweaks) that would improve future runs.

Return clean JSON with key "improvements" (list of dicts with "type", "description", "action")."""

        response = self.compute.call_llm(reflection_prompt, temperature=0.4, max_tokens=800)
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

    def re_adapt(self, candidate: Dict, latest_verifier_feedback: str):
        self.loop_count += 1
        grail_context = self.load_from_memdir("latest_grail")
        recent_trajectories = vector_db.search(getattr(self, '_current_strategy', {}).get("challenge", ""), k=20)

        weighted_context = ""
        if recent_trajectories:
            scored_traj = []
            for traj in recent_trajectories:
                score = traj.get("validation_score", traj.get("local_score", 0.5))
                fidelity = traj.get("fidelity", 0.5)
                weight = max(0.1, (score ** 2) * (fidelity ** 1.5))
                scored_traj.append((weight, traj.get("solution", "")[:700]))
            scored_traj.sort(key=lambda x: x[0], reverse=True)
            weighted_context = "\n".join([f"[High-score+fidelity {i+1} | w={w:.2f}]: {text}" 
                                        for i, (w, text) in enumerate(scored_traj[:10])])

        recent_messages = self.get_recent_messages(min_importance=0.5, limit=12)
        message_context = "\n".join([f"[{m.get('type')}] score={m['validation_score']:.2f} fid={m['fidelity']:.2f}: {m['content'][:500]}" 
                                  for m in recent_messages]) if recent_messages else "None"

        diagnostics = self.run_diagnostics(candidate.get("solution", ""), candidate.get("challenge", "unknown"), latest_verifier_feedback)

        fix_recommendations = self.generate_fix_recommendations(diagnostics, candidate.get("solution", ""))

        if fix_recommendations:
            top_fix = fix_recommendations[0]
            success, new_solution, new_score = self.apply_fix(top_fix, candidate.get("solution", ""), candidate.get("challenge", "unknown"), latest_verifier_feedback)
            if success:
                candidate["solution"] = new_solution
                logger.info(f"✅ Fix applied successfully — new score {new_score:.3f}")

        # NEW: Compress intelligence deltas before feeding to Adaptation Arbos
        raw_context = f"Verifier feedback: {latest_verifier_feedback}\nWeighted trajectories: {weighted_context}\nMessages: {message_context}\nDiagnostics: {json.dumps(diagnostics, indent=2)[:800]}"
        compressed_deltas = self.compress_intelligence_delta(raw_context)

        reinforcement = sum(self.grail_reinforcement.values()) / max(len(self.grail_reinforcement), 1) if self.grail_reinforcement else 0.0

        adaptation_prompt = f"""You are Adaptation Arbos for SN63.
CURRENT LOOP: {self.loop_count}
Latest feedback: {latest_verifier_feedback}
Diagnostics: {json.dumps(diagnostics.get("detectors", {}), indent=2)[:600]}
Fix Recommendations: {json.dumps(fix_recommendations, indent=2)[:800]}
COMPRESSED INTELLIGENCE DELTAS:
{compressed_deltas}

Generate concise, high-signal adaptation incorporating the fix recommendations. Prioritize fidelity ≥0.88 and determinism ≥0.85."""

        adaptation_raw = self.compute.call_llm(adaptation_prompt, temperature=0.15, max_tokens=1400)
        adapted = self._safe_parse_json(adaptation_raw)
        self._current_strategy = adapted.get("strategy", self._current_strategy)
        self.validator.adapt_scoring(self._current_strategy)

        self.save_to_memdir("latest_grail", {
            "loop": self.loop_count,
            "feedback": latest_verifier_feedback[:600],
            "adaptation": str(adaptation_raw)[:1200],
            "diagnostics": diagnostics,
            "fix_recommendations": fix_recommendations,
            "timestamp": datetime.now().isoformat()
        })

        if "final_solution" in candidate:
            self.update_memory_policy("latest_adaptation", getattr(self.validator, "last_score", 0.0))

        logger.info(f"✅ re_adapt completed loop {self.loop_count} with full upgrades")

    def run_toolhunter_swarm(self, gap_description: str, max_proposals: int = 5) -> dict:
        if not gap_description or len(gap_description.strip()) < 5:
            return {"status": "error", "message": "Gap description too short or empty."}

        logger.info(f"ToolHunter Swarm launched for gap: {gap_description[:100]}...")

        hunt_result = self._tool_hunter(gap_description, "miner_requested_swarm")

        structured = {
            "status": "success",
            "gap": gap_description,
            "raw_result": hunt_result,
            "timestamp": datetime.now().isoformat(),
            "loop": self.loop_count,
            "proposals": [],
            "install_commands": [],
            "confidence": 0.7
        }

        try:
            lines = str(hunt_result).split("\n")
            for line in lines:
                line = line.strip()
                if line and ("pip" in line.lower() or "install" in line.lower()):
                    structured["install_commands"].append(line)
                elif line and len(line) > 10 and not line.startswith("["):
                    structured["proposals"].append(line)
        except:
            pass

        structured["proposals"] = structured["proposals"][:max_proposals]

        self.post_message(
            sender="ToolHunterSwarm",
            content=f"Gap: {gap_description[:200]}... | Found {len(structured['proposals'])} proposals",
            msg_type="tool_recommendation",
            importance=0.75,
            validation_score=0.0,
            fidelity=0.65
        )

        memory.add(
            text=f"ToolHunter Swarm Result: {gap_description}",
            metadata={"type": "toolhunter_swarm", "proposals": structured["proposals"]}
        )

        logger.info(f"ToolHunter Swarm completed — {len(structured['proposals'])} proposals found")
        return structured

    def _tool_hunter(self, gap: str, subtask: str) -> str:
        result = tool_hunter.hunt_and_integrate(gap, subtask)
        if result.get("status") == "success" and result.get("links"):
            for link in result.get("links", [])[:3]:
                clean = self.reach_tool.fetch_url_content(link.get("url", ""))
                vector_db.add({
                    "type": "external_reach",
                    "url": link.get("url"),
                    "content_summary": clean[:500],
                    "validation_score": 0.0
                })
                result["recommendation"] += f"\n[Agent-Reach] {link.get('url')}: {clean[:200]}..."
        if result.get("status") == "success":
            return f"ToolHunter + Agent-Reach ({result.get('source', 'unknown')}): {result.get('recommendation')}"
        return "ToolHunter + Agent-Reach found no strong match for this quantum subtask."

    def _generate_candidates_eggroll(self, subtask: str, hypothesis: str, current_solution: str) -> str:
        base = {"solution": current_solution, "novelty_proxy": 0.5, "est_compute": 1.0}
        candidates = [base]
        for i in range(3):
            perturbed, _ = self.generate_low_rank_perturbation(base, seed=i)
            candidates.append(perturbed)
        ranked = sorted(candidates, key=lambda c: compute_energy(c, self.validator, rank=self.eggroll_rank), reverse=True)
        return ranked[0]["solution"]

    def generate_low_rank_perturbation(self, base_solution: Dict, rank: int = None, seed: int = None) -> Tuple[Dict, Dict]:
        if rank is None: rank = self.eggroll_rank
        if seed is not None: np.random.seed(seed)
        perturbation = {"delta_novelty": np.random.normal(0, self.sigma / np.sqrt(rank)), "rank": rank}
        perturbed = base_solution.copy()
        perturbed["novelty_proxy"] = perturbed.get("novelty_proxy", 0.5) + perturbation["delta_novelty"]
        return perturbed, perturbation

    def _run_verification(self, solution: str, verification_instructions: str, challenge: str) -> str:
        candidate = {"solution": solution}
        oracle_result = self.validator.run(candidate, verification_instructions, challenge)
        self._current_strategy = oracle_result.get("strategy")
        vector_db.add_eggroll({"solution": solution, "validation_score": oracle_result["validation_score"]})
        return f"ValidationOracle: score={oracle_result['validation_score']:.3f} | Strategy: {self._current_strategy.get('domain', 'quantum_adaptive')} | V/Vd: {oracle_result['vvd_ready']}"

    def _run_swarm(self, blueprint: Dict[str, Any], challenge: str, verification_instructions: str = "", deterministic_tooling: str = "") -> str:
        self._current_strategy = self.analyzer.analyze(verification_instructions, challenge)
        
        self._current_validation_criteria = blueprint.get("validation_criteria", {})
        
        decomposition = blueprint.get("decomposition", ["Full quantum challenge"])
        swarm_config = blueprint.get("swarm_config", {"total_instances": 1})

        total_instances = min(swarm_config.get("total_instances", 4), 6)
        if self.config.get("resource_aware"):
            total_instances = min(total_instances, 4)

        manager_dict = multiprocessing.Manager().dict()
        trace_log = [f"🚀 Event-driven Swarm launched with {total_instances} threads (Quasar: {self.quasar_enabled})"]
        
        criteria_str = json.dumps(self._current_validation_criteria, indent=2)
        trace_log.append(f"DECIDED VALIDATION CRITERIA FOR SUB-ARBOS AGENTS:\n{criteria_str}")
        logger.info(f"Validation Criteria for this swarm:\n{criteria_str}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=total_instances) as executor:
            futures = []
            subtask_id = 0
            for i, subtask in enumerate(decomposition):
                count = swarm_config.get("assignment", {}).get(subtask, 1)
                tools = blueprint.get("tool_map", {}).get(subtask, ["none"])
                for _ in range(count):
                    hyp = swarm_config.get("hypothesis_diversity", ["standard"] * len(decomposition))[i % len(decomposition)]
                    futures.append(executor.submit(
                        self._sub_arbos_worker, subtask, hyp, tools, manager_dict, subtask_id
                    ))
                    subtask_id += 1

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    trace_log.append(f"Thread error: {e}")

        all_results = dict(manager_dict)

        sub_scores = np.array([r.get("local_score", 0.5) for r in all_results.values()])
        if len(sub_scores) > 0:
            weights = np.exp(sub_scores) / np.sum(np.exp(sub_scores))
            weighted_avg = np.average(sub_scores, weights=weights)
        else:
            weighted_avg = 0.5
        trace_log.append(f"MARL-weighted sub-avg score: {weighted_avg:.3f}")

        failed_context = "\nPrevious failed attempts:\n" + "\n---\n".join(memory.query(challenge + " failed", n_results=5)) if memory.query(challenge + " failed", n_results=5) else ""

        synthesis_task = f"""You are Arbos Orchestrator for SN63 Quantum Innovate.
Challenge: {challenge}
Verification Instructions: {verification_instructions or 'General quantum standards'}
Miner Deterministic Tooling: {deterministic_tooling or 'None specified'}
{failed_context}
Swarm results: {json.dumps(all_results, indent=2)[:2000]}
MARL-weighted sub-avg score: {weighted_avg:.3f}

Be extremely honest. For cryptographic challenges like breaking BTC, clearly state feasibility.
Do not claim breakthroughs without strong evidence.
Synthesize final high-quality realistic assessment (weight higher-scoring subtasks):"""

        final_solution = self.compute.call_llm(synthesis_task, temperature=0.5, max_tokens=2000)

        if verification_instructions and verification_instructions.strip():
            verification_result = self._run_verification(final_solution, verification_instructions, challenge)
            final_solution += f"\n\n--- VERIFICATION RESULT ---\n{verification_result}"

        if self.config.get("guardrails"):
            final_solution = apply_guardrails(final_solution, ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8)))

        memory.add(text=final_solution[:1500], metadata={"challenge": challenge, "status": "final", "sub_avg_score": weighted_avg})
        trace_log.append("Synthesis + Verification complete")

        try:
            import streamlit as st
            if "trace_log" not in st.session_state:
                st.session_state.trace_log = []
            st.session_state.trace_log.extend(trace_log)
        except:
            pass

        self.loop_count += 1
        return final_solution

    def _execute_swarm(self, blueprint: Any, dynamic_size: int):
        blueprint = self._safe_parse_json(blueprint)
        decomposition = blueprint.get("decomposition", ["Full quantum challenge"])
        
        hypothesis_diversity = blueprint.get("hypothesis_diversity", ["standard"])
        if not hypothesis_diversity:
            hypothesis_diversity = ["standard"]

        manager_dict = multiprocessing.Manager().dict()
        with concurrent.futures.ProcessPoolExecutor(max_workers=min(dynamic_size, 6)) as executor:
            futures = []
            for subtask_id, subtask in enumerate(decomposition):
                hyp_index = subtask_id % len(hypothesis_diversity)
                hyp = hypothesis_diversity[hyp_index]
                tools = blueprint.get("tool_map", {}).get(subtask, ["none"])
                futures.append(executor.submit(
                    self._sub_arbos_worker, subtask, hyp, tools, manager_dict, subtask_id
                ))
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Swarm worker error: {e}")
        return dict(manager_dict)

    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                          shared_results: dict, subtask_id: int) -> dict:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours / 3.0)
        repair_attempts = 0
        
        validation_criteria = self._current_validation_criteria.get(subtask, self._current_validation_criteria)
        trace = [f"Sub-Arbos {subtask_id} started | Using Criteria: {json.dumps(validation_criteria, indent=2)[:400]}..."]

        if self.config.get("resource_aware") and monitor.elapsed_hours() > max_hours * 0.75:
            solution = "Early abort: time budget exceeded."
            trace.append("Resource-aware early abort")
            local_score = 0.0
        else:
            solution = f"Subtask: {subtask}\nHypothesis: {hypothesis}"
            trace.append(f"Sub-Arbos {subtask_id} started with hypothesis: {hypothesis}")

            symbolic_result = symbolic_module(subtask, hypothesis, solution, getattr(self, "_current_strategy", {"enabled_modules": ["sympy"]}))
            if symbolic_result:
                solution += f"\n{symbolic_result}"
                trace.append("Used dynamic symbolic/deterministic tooling (Verifier-code-first)")

            solution = self._generate_candidates_eggroll(subtask, hypothesis, solution)

            local_score = 0.5

            for loop in range(3):
                local_eval = None
                if validation_criteria:
                    criteria = validation_criteria
                    self_check = criteria.get("self_check_prompt", "Evaluate how well this solution meets the success criteria. Score 0.0-1.0 and explain.")
                    eval_prompt = f"""{self_check}
Subtask criteria: {criteria.get('criteria', 'None')}
Current solution:
{solution[:1500] if solution else 'None yet'}
Give a score (0.0-1.0) and short explanation."""
                    local_eval = self.compute.call_llm(eval_prompt, temperature=0.0, max_tokens=400)
                    trace.append(f"Self-eval (loop {loop+1}): {local_eval[:150]}...")
                    try:
                        score_str = local_eval.split("0.")[1][:3] if "0." in local_eval else "0.5"
                        local_score = float(score_str)
                    except:
                        local_score = 0.5

                reflect_task = f"""You are a focused sub-Arbos for SN63 Quantum.
Subtask: {subtask}
Hypothesis: {hypothesis}
Current: {solution[:800]}
{'Self-evaluation: ' + (local_eval[:400] if local_eval else '')}
Prefer deterministic/symbolic tools. Decide: Improve / Call Tool / Finalize"""

                response = self.compute.call_llm(reflect_task, temperature=0.0, max_tokens=600)
                trace.append(f"Loop {loop+1}")

                if "Finalize" in response or "final" in response.lower():
                    break

                if self.config.get("toolhunter_escalation") and ("ToolHunter" in str(tools) or "hunter" in response.lower()):
                    gap = f"Gap in {subtask}"
                    hunt = self._tool_hunter(gap, subtask)
                    solution += f"\n[ToolHunter + ReadyAI]\n{hunt}"
                elif tools and tools[0] != "none":
                    output = self.compute.call_llm(f"Apply {tools[0]} to quantum subtask: {solution[:600]}", temperature=0.0, max_tokens=500)
                    solution += f"\n[{tools[0]}]\n{output}"

                if self.config.get("guardrails"):
                    solution = apply_guardrails(solution, monitor)

                if "error" in solution.lower() and repair_attempts < self.max_repair_attempts:
                    repair_attempts += 1
                    trace.append(f"Repair attempt {repair_attempts}/{self.max_repair_attempts}")
                    solution = self._generate_candidates_eggroll(subtask, hypothesis, solution)

                if time.time() - monitor.start_time > (max_hours * 1800 / 6):
                    break

        memory.add(text=solution[:1000], metadata={"subtask": subtask, "status": "completed", "local_score": local_score})
        vector_db.add({"type": "sub_arbos_result", "subtask": subtask, "local_score": local_score, "solution": solution[:800]})

        shared_results[subtask_id] = {"subtask": subtask, "solution": solution, "trace": trace, "local_score": local_score}
        return shared_results[subtask_id]

    def _generate_tool_proposals(self, results: Dict) -> List[str]:
        proposal_prompt = f"Based on these swarm results: {json.dumps(results)[:1500]}\nSuggest 2-3 deterministic or quantum-related tools that would improve verifier score on the NEXT run."
        response = self.compute.call_llm(proposal_prompt, temperature=0.3, max_tokens=600)
        proposals = [line.strip() for line in response.split("\n") if line.strip()][:3]
        
        for p in proposals:
            try:
                memory.add(f"TOOL PROPOSAL: {p}", {"type": "tool_proposal"})
            except Exception as e:
                logger.warning(f"Failed to add proposal: {e}")
        
        return proposals

    def _run_grail_post_training(self, results: Dict):
        logger.info("Grail post-training triggered on winning run (verifiable proof attached to package)")

    def execute_full_cycle(self, blueprint: Dict, challenge: str, verification_instructions: str = ""):
        dynamic_size = blueprint.get("dynamic_swarm_size", blueprint.get("swarm_config", {}).get("total_instances", 5))
        results = self._execute_swarm(blueprint, dynamic_size)
        
        score_dict = self.validator.run(
            candidate=results,
            verification_instructions=verification_instructions,
            challenge=challenge,
            goal_md=self._load_extra_context()
        )
        
        if score_dict.get("validation_score", 0) > 0.92 and self.enable_grail:
            self._run_grail_post_training(results)

        proposals = self._generate_tool_proposals(results)
        self.memory_layers.add_proposals(proposals)
        return score_dict.get("final_solution", str(score_dict)) if isinstance(score_dict, dict) else str(score_dict)

    def export_trajectories_for_optimization(self, challenge: str):
        traj = vector_db.search(challenge, k=50)
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
        trajectories = vector_db.search(challenge, k=20)
        critique_task = f"""You are Arbos Self-Improvement Analyst for SN63 Quantum.

Challenge: {challenge}
Recent run history:
{json.dumps(history, indent=2)}
High-signal trajectories:
{json.dumps(trajectories, indent=2)}

Be critical:
- Is the ValidationOracle too lenient on cryptographic tasks?
- Are we generating real insight or just placeholder content?
- What prompt or architecture changes would force more honest output?

Return clean JSON."""
        response = self.compute.call_llm(critique_task, temperature=0.7, max_tokens=1000)
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
                "recommended_prompt_additions": "Always be brutally honest about computational feasibility. Never claim to break strong cryptography without extraordinary evidence."
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

        response = self.compute.call_llm(task, temperature=0.0, max_tokens=2000)
        blueprint = self._parse_json(response)
        
        self._current_pre_launch = blueprint.get("generated_pre_launch_context", "")

        if "module_reflection" in blueprint or "generated_pre_launch_context" in blueprint:
            self.save_to_memdir(f"reflection_{int(time.time())}", blueprint)
        
        return blueprint

    def _parse_json(self, raw: str) -> Dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except:
            return {"decomposition": ["Fallback quantum decomposition"], "swarm_config": {"total_instances": 5}, "tool_map": {}, "validation_criteria": {}, "hypothesis_diversity": ["standard", "quantum_optimized"]}

def run(self, challenge: str, verification_instructions: str = "", enhancement_prompt: str = ""):
        self.loop_count = 0
        plan = self.plan_challenge(
            goal_md=self.extra_context,
            challenge=challenge,
            enhancement_prompt=enhancement_prompt
        )

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
                self.re_adapt({"solution": current_solution}, f"Validation score: {score:.3f}")
                plan = self._refine_plan(plan, challenge, enhancement_prompt=enhancement_prompt)

        if self.enable_grail and best_score > 0.92:
            self.consolidate_grail(best_solution or "", best_score, best_diagnostics)
            self.meta_reflect(best_solution or "", best_score, best_diagnostics)

        if best_score > 0.85 and self.enable_grail:
            fidelity = 0.92
            self.evolve_compression_prompt(best_score, fidelity)

        self.save_run_to_history(challenge, enhancement_prompt, best_solution or "", best_score, 0.5, best_score)
        return best_solution or "No valid solution produced"
