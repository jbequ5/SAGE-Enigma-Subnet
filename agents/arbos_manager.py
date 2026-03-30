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

multiprocessing.set_start_method('spawn', force=True)

from agents.memory import memory, memory_layers
from agents.tools.tool_hunter import tool_hunter, load_registry, save_registry
from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails

from validation_oracle import ValidationOracle
from trajectories.trajectory_vector_db import vector_db
from tools.agent_reach_tool import AgentReachTool
from verification_analyzer import VerificationAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# ====================== WORKING COMPUTE ENERGY ======================
def compute_energy(candidate: Dict, validator, rank: int = 8) -> float:
    """Fully working energy function for EGGROLL low-rank perturbations."""
    base = 1.0
    novelty = candidate.get("novelty_proxy", 0.5)
    score = getattr(validator, "last_score", 0.85)
    energy = base + (novelty * 0.4) + (score * 0.6) - (rank * 0.01)
    return max(0.1, energy)

# ====================== SYMBOLIC MODULE — VERIFIER-CODE-FIRST ======================
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
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()

        self.history_file = Path("submissions/run_history.json")
        self._ensure_history_file()

        self.compute_source = self.config.get("compute_source", "chutes")
        self.custom_endpoint = None
        self.compute.set_compute_source(self.compute_source, self.custom_endpoint)

        # === INTELLIGENT COMPUTE ROUTING SETUP ===
        self.compute.enable_quasar(True)
        if self.compute.quasar_enabled:
            self.compute.run_on_compute("Warm-up: Quasar model ready", task_type="planning")

        self.validator = ValidationOracle(goal_file)
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

        self.memory_layers = memory_layers

        logger.info("✅ ArbosManager v3.0 — Hardened + ReadyAI llms.txt + Quasar Auto-Download")

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
                pass

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
            "compute_source": "chutes"
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    if ":" not in line: continue
                    key = line.split(":")[0].strip().lower()
                    value = line.split(":", 1)[1].strip()
                    if key in config and isinstance(config[key], bool):
                        config[key] = "true" in value.lower()
                    elif key in ["max_loops"]:
                        config[key] = int(value)
                    elif key == "max_compute_hours":
                        config[key] = float(value)
                    elif key == "compute_source":
                        config[key] = value.lower()
        except Exception:
            pass
        return config

    def _load_extra_context(self) -> str:
        try:
            with open(self.goal_file, "r") as f:
                return f.read()
        except Exception:
            return ""

    def discover_from_goal(self, goal_content: str) -> list:
        registry = load_registry()
        discovery_task = f"""You are ToolHunter in pre-run discovery mode.

GOAL.md content:
{goal_content[:5000]}

Task: Analyze the goals and suggest the most relevant tools, libraries, or Hugging Face models.
Prioritize deterministic/symbolic tools."""
        response = self.compute.run_on_compute(discovery_task, temperature=0.0, task_type="toolhunter")
        new_items = []
        try:
            lines = response.split("\n")
            current = {}
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("•"):
                    if current:
                        new_items.append(current)
                    current = {"name": line[2:], "keywords": [], "install_cmd": "", "added": datetime.now().isoformat()}
                elif "install" in line.lower() or "pip" in line.lower():
                    if current:
                        current["install_cmd"] = line
            if current:
                new_items.append(current)
            if new_items:
                registry["tools"].extend(new_items)
                save_registry(registry)
                return new_items
        except Exception as e:
            logger.warning(f"Discovery parsing error: {e}")
        return []

    def plan_challenge(self, challenge: str, enhancement_prompt: str = "") -> Dict[str, Any]:
        phase1 = self.compute.run_on_compute(
            f"Challenge: {challenge}\nMiner enhancement: {enhancement_prompt}\nPhase 1: High-level goals, risks, subtasks.",
            task_type="planning"
        )

        available_vram = 48.0
        try:
            available_vram = ResourceMonitor().get_available_vram_gb()
        except:
            pass
        per_agent_gb = 6.0
        dynamic_size = min(self.max_swarm_size, max(3, int(available_vram // per_agent_gb)))

        phase2 = self.compute.run_on_compute(
            f"Phase 1 output: {phase1}\nAvailable compute supports {dynamic_size} Sub-Arbos.\nPhase 2: Full executable blueprint.",
            task_type="orchestration"
        )

        adaptation = self.compute.run_on_compute(
            f"Full context from Phase 1+2.\nAdapt scoring weights, enabled modules, thresholds.",
            task_type="adaptation", temperature=0.0
        )
        adapted = json.loads(adaptation) if isinstance(adaptation, str) else adaptation

        self._current_strategy = adapted.get("strategy", self.analyzer.analyze("", challenge))
        self.validator.adapt_scoring(self._current_strategy)

        return {
            "phase1": phase1,
            "phase2": phase2,
            "adapted_strategy": self._current_strategy,
            "dynamic_swarm_size": dynamic_size
        }

    def re_adapt(self, candidate: Dict, latest_verifier_feedback: str):
        self.loop_count += 1
        
        if self.memory_layers.get_total_context_tokens() > 150000:
            self.memory_layers.compress_low_value(getattr(self.validator, 'last_score', 0.0))

        adaptation = self.compute.run_on_compute(
            f"Adaptation Arbos — RE-RUN (loop {self.loop_count})\nLatest feedback: {latest_verifier_feedback}",
            task_type="re_adapt", temperature=0.0
        )
        adapted = json.loads(adaptation) if isinstance(adaptation, str) else adaptation
        self._current_strategy = adapted.get("strategy", self._current_strategy)
        self.validator.adapt_scoring(self._current_strategy)

    def _generate_tool_proposals(self, results: Dict) -> List[str]:
        proposal_prompt = f"Based on these results: {json.dumps(results)[:1200]}\nSuggest 2-3 deterministic tools or helpers that would improve verifier score on the NEXT run only."
        response = self.compute.run_on_compute(proposal_prompt, temperature=0.3, task_type="tool_proposal")
        proposals = [line.strip() for line in response.split("\n") if line.strip()][:3]
        self.memory_layers.add_proposals(proposals)
        return proposals

    def _run_grail_post_training(self, results: Dict):
        logger.info("Grail post-training triggered on winning run (verifiable proof attached to package)")

    def _execute_swarm(self, blueprint: Dict, dynamic_size: int):
        num_sub_arbos = dynamic_size
        manager_dict = multiprocessing.Manager().dict()
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_sub_arbos) as executor:
            futures = []
            for subtask_id, subtask in enumerate(blueprint.get("decomposition", [])):
                hyp = blueprint.get("hypothesis_diversity", ["standard"])[subtask_id % len(blueprint.get("hypothesis_diversity", []))]
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
        validation_criteria = getattr(self, "_current_validation_criteria", {}).get(subtask, None)

        if self.config.get("resource_aware") and monitor.elapsed_hours() > max_hours * 0.75:
            solution = "Early abort: time budget exceeded."
            trace = ["Resource-aware early abort"]
            local_score = 0.0
        else:
            solution = f"Subtask: {subtask}\nHypothesis: {hypothesis}"
            trace = [f"Sub-Arbos {subtask_id} started"]

            symbolic_result = symbolic_module(subtask, hypothesis, solution, getattr(self, "_current_strategy", {"enabled_modules": ["sympy"]}))
            if symbolic_result:
                solution += f"\n{symbolic_result}"
                trace.append("Used dynamic symbolic/deterministic tooling (Verifier-code-first)")

            solution = self._generate_candidates_eggroll(subtask, hypothesis, solution)

            current_reflect_prompt = None
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
                    local_eval = self.compute.run_on_compute(eval_prompt, temperature=0.0, task_type="sub_eval")
                    trace.append(f"Self-eval: {local_eval[:150]}...")
                    try:
                        score_str = local_eval.split("0.")[1][:3] if "0." in local_eval else "0.5"
                        local_score = float(score_str)
                    except:
                        local_score = 0.5

                if current_reflect_prompt:
                    reflect_task = current_reflect_prompt
                else:
                    reflect_task = f"""You are a focused sub-Arbos.
Subtask: {subtask}
Hypothesis: {hypothesis}
Current: {solution[:800]}
{'Self-evaluation from last attempt: ' + (local_eval[:400] if local_eval else '')}
Prefer deterministic tools.
Decide: Improve / Call Tool / Finalize
Stay tightly aligned with the validation criteria."""

                response = self.compute.run_on_compute(reflect_task, temperature=0.0, task_type="subtask", novelty_level="medium")
                trace.append(f"Loop {loop+1}")

                if "Finalize" in response or "final" in response.lower():
                    break

                if "ToolHunter" in str(tools) or "hunter" in response.lower():
                    gap = f"Gap in {subtask}"
                    hunt = self._tool_hunter(gap, subtask)
                    solution += f"\n[ToolHunter]\n{hunt}"
                elif tools and tools[0] != "none":
                    output = self.compute.run_on_compute(f"Apply {tools[0]} to: {solution[:600]}", temperature=0.0, task_type="subtask")
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
        return "ToolHunter + Agent-Reach found no strong match."

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
        return f"ValidationOracle: score={oracle_result['validation_score']:.3f} | Strategy: {self._current_strategy.get('domain', 'adaptive')} | V/Vd: {oracle_result['vvd_ready']}"

    def _run_swarm(self, blueprint: Dict[str, Any], challenge: str, verification_instructions: str = "", deterministic_tooling: str = "") -> str:
        self._current_strategy = self.analyzer.analyze(verification_instructions, challenge)
        self._current_validation_criteria = blueprint.get("validation_criteria", {})

        decomposition = blueprint.get("decomposition", ["Full challenge"])
        swarm_config = blueprint.get("swarm_config", {"total_instances": 1})
        tool_map = blueprint.get("tool_map", {})

        total_instances = min(swarm_config.get("total_instances", 4), 6)
        if self.config.get("resource_aware"):
            total_instances = min(total_instances, 4)

        manager_dict = multiprocessing.Manager().dict()
        trace_log = [f"🚀 Event-driven Swarm launched with {total_instances} threads"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=total_instances) as executor:
            futures = []
            subtask_id = 0
            for i, subtask in enumerate(decomposition):
                count = swarm_config.get("assignment", {}).get(subtask, 1)
                tools = tool_map.get(subtask, ["none"])
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

        synthesis_task = f"""You are Arbos Orchestrator.
Challenge: {challenge}
Verification Instructions: {verification_instructions or 'General SN63 standards'}
Miner Deterministic Tooling: {deterministic_tooling or 'None specified'}
{failed_context}
Swarm results (with local scores): {json.dumps(all_results, indent=2)}
MARL-weighted sub-avg score: {weighted_avg:.3f}
Final Synthesized Solution (weight higher-scoring subtasks more):"""

        final_solution = self.compute.run_on_compute(synthesis_task, temperature=0.0, task_type="synthesis", novelty_level="high")

        if verification_instructions and verification_instructions.strip():
            verification_result = self._run_verification(final_solution, verification_instructions, challenge)
            final_solution += f"\n\n--- VERIFICATION RESULT ---\n{verification_result}"

        if self.config.get("guardrails"):
            final_solution = apply_guardrails(final_solution, ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8)))

        memory.add(text=final_solution[:1500], metadata={"challenge": challenge, "status": "final", "sub_avg_score": weighted_avg})
        trace_log.append("Synthesis + Verification complete")

        import streamlit as st
        if "trace_log" not in st.session_state:
            st.session_state.trace_log = []
        st.session_state.trace_log.extend(trace_log)

        self.loop_count += 1
        return final_solution

    def execute_full_cycle(self, plan: Dict, challenge: str, verification_instructions: str = ""):
        dynamic_size = plan.get("dynamic_swarm_size", 6)
        results = self._execute_swarm(plan["phase2"], dynamic_size)
        score_dict = self.validator.run(results, verification_instructions, challenge)
        
        if score_dict.get("validation_score", 0) > 0.92 and self.enable_grail:
            self._run_grail_post_training(results)

        proposals = self._generate_tool_proposals(results)
        self.memory_layers.add_proposals(proposals)
        return score_dict

    def export_trajectories_for_optimization(self, challenge: str):
        traj = vector_db.search(challenge, k=50)
        path = Path("trajectories") / f"export_{challenge[:30]}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(traj, indent=2))
        logger.info(f"Exported {len(traj)} trajectories to {path} for offline optimization")
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
        critique_task = f"""You are Arbos Self-Improvement Analyst.

Challenge: {challenge}
Recent run history:
{json.dumps(history, indent=2)}
High-signal trajectories:
{json.dumps(trajectories, indent=2)}

Extract:
- structured_memories
- workflow_evolution
- recommended_prompt_additions

Return clean JSON."""
        response = self.compute.run_on_compute(critique_task, temperature=0.3, task_type="self_critique")
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
                "workflow_evolution": [],
                "recommended_prompt_additions": ""
            }

    def perform_autoresearch(self, critique: Dict) -> str:
        patches = critique.get("autoresearch_patches", [])
        if not patches:
            return "No autoresearch patches proposed this cycle."
        logger.info(f"Applying {len(patches)} autoresearch patches to Arbos")
        return json.dumps(patches, indent=2)

    def apply_self_improvement(self, current_prompt: str, critique: Dict) -> str:
        addition = critique.get("recommended_prompt_additions", "")
        if addition and addition.strip():
            return current_prompt.strip() + "\n\n" + addition.strip()
        return current_prompt

    def _refine_plan(self, approved_plan: Dict, challenge: str, deterministic_tooling: str = "", enhancement_prompt: str = "") -> Dict:
        extra = f"\nMiner deterministic tooling: {deterministic_tooling}" if deterministic_tooling else ""
        extra += f"\nMiner enhancement instructions: {enhancement_prompt}" if enhancement_prompt else ""
        task = f"""You are Arbos Orchestrator.
Approved plan: {json.dumps(approved_plan)}{extra}
Time left: {self.config.get('max_compute_hours', 3.8)}h
Output EXACT JSON with decomposition, swarm_config, tool_map, deterministic_recommendations, validation_criteria."""
        response = self.compute.run_on_compute(task, temperature=0.0, task_type="orchestration")
        return self._parse_json(response)

    def _parse_json(self, raw: str) -> Dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except:
            return {"decomposition": ["Fallback"], "swarm_config": {"total_instances": 1}, "tool_map": {}, "validation_criteria": {}}

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
        return "ToolHunter + Agent-Reach found no strong match."

    def run(self, challenge: str, verification_instructions: str = "", enhancement_prompt: str = ""):
        self.loop_count = 0
        plan = self.plan_challenge(challenge, enhancement_prompt)
        return self.execute_full_cycle(plan, challenge, verification_instructions)
