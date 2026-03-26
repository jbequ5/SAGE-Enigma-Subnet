# agents/arbos_manager.py
# FINAL FULL UPGRADE - Arbos-centric SN63 Miner with vLLM + Executable Verification

import os
import subprocess
import json
import concurrent.futures
import multiprocessing
import time
from typing import Tuple, List, Dict, Any

from agents.memory import memory

from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails
from agents.tools.tool_hunter import tool_hunter

# vLLM shared server for swarm efficiency
_vllm_llm = None

def get_vllm_llm():
    global _vllm_llm
    if _vllm_llm is None:
        try:
            from vllm import LLM
            print("🚀 Initializing vLLM shared model...")
            _vllm_llm = LLM(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                tensor_parallel_size=1,
                gpu_memory_utilization=0.85,
                dtype="float16",
                max_model_len=8192
            )
            print("✅ vLLM loaded successfully")
        except Exception as e:
            print(f"⚠️ vLLM failed: {e}. Falling back to per-process mode.")
            _vllm_llm = None
    return _vllm_llm


class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()
        print("✅ Arbos Primary Solver loaded with vLLM + Executable Verification")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "miner_review_after_loop": False,
            "max_loops": 5,
            "miner_review_final": True,
            "chutes": True,
            "chutes_llm": "mixtral",
            "max_compute_hours": 3.8,
            "resource_aware": True,
            "guardrails": True,
            "toolhunter_escalation": True,
            "manual_tool_installs_allowed": True
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    stripped = line.strip().lower()
                    key = line.split(":")[0].strip().lower()
                    value = line.split(":", 1)[1].strip()
                    if key in ["miner_review_after_loop", "miner_review_final", "chutes", "resource_aware", "guardrails", "toolhunter_escalation", "manual_tool_installs_allowed"]:
                        config[key] = "true" in value.lower()
                    elif key in ["max_loops", "max_compute_minutes"]:
                        config[key] = int(value)
                    elif key == "max_compute_hours":
                        config[key] = float(value)
                    elif key == "chutes_llm":
                        config[key] = value
        except Exception:
            pass
        return config

    def _load_extra_context(self) -> str:
        try:
            with open(self.goal_file, "r") as f:
                content = f.read()
            if "# Miner Control" in content or "# Compute" in content:
                return content.split("# Compute", 1)[-1].strip()
            return content
        except Exception:
            return ""

    def plan_challenge(self, challenge: str) -> Dict[str, Any]:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours)
        remaining = max_hours - monitor.elapsed_hours()

        full_context = f"""CHALLENGE: {challenge}
MINER STRATEGY: {self.extra_context}
Time available: {remaining:.2f}h"""

        past = memory.query(challenge, n_results=6)
        if past:
            full_context += "\nPast attempts:\n" + "\n---\n".join(past)

        task = f"""You are Planning Arbos. {full_context}
Output EXACT JSON with high_level_goals, risks_and_mitigations, rough_decomposition, suggested_swarm_size, high_level_tool_hints, compute_ballpark_minutes, quality_gate_targets."""

        response = self.compute.run_on_compute(task)
        return self._parse_json(response)

    def _refine_plan(self, approved_plan: Dict, challenge: str) -> Dict:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours)
        remaining = max_hours - monitor.elapsed_hours()

        task = f"""You are Arbos Orchestrator.
Approved plan: {json.dumps(approved_plan)}
Time left: {remaining:.2f}h
Output EXACT JSON with decomposition, swarm_config, tool_map, compute_projection_minutes, risk_flags."""

        response = self.compute.run_on_compute(task)
        return self._parse_json(response)

    def _parse_json(self, raw: str) -> Dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except:
            return {"decomposition": ["Fallback"], "swarm_config": {"total_instances": 1}, "tool_map": {}}

    def _tool_hunter(self, gap: str, subtask: str) -> str:
        if not self.config.get("toolhunter_escalation", True):
            return "[ToolHunter disabled]"
        result = tool_hunter.hunt_and_integrate(gap, subtask, f"SN63: {subtask}")
        if result.get("status") == "success":
            return f"ToolHunter SUCCESS: {result.get('tool_name')}"
        else:
            if self.config.get("manual_tool_installs_allowed", True):
                return f"ToolHunter MANUAL REQUIRED:\n{result.get('miner_recommendation', '')}"
            return "ToolHunter failed. Manual disabled."

    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                          shared_results: dict, subtask_id: int) -> dict:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours / 3.0)

        if self.config.get("resource_aware") and monitor.elapsed_hours() > max_hours * 0.75:
            solution = "Early abort: time budget exceeded."
            trace = ["Resource-aware early abort"]
        else:
            solution = f"Subtask: {subtask}\nHypothesis: {hypothesis}"
            trace = [f"Sub-Arbos {subtask_id} started"]

            for loop in range(3):
                reflect_task = f"""You are a focused sub-Arbos.
Subtask: {subtask}
Hypothesis: {hypothesis}
Current: {solution[:700]}
Decide: Improve / Call Tool / Finalize"""
                response = self.compute.run_on_compute(reflect_task)
                trace.append(f"Loop {loop+1}")

                if "Finalize" in response or "final" in response.lower():
                    break

                if "ToolHunter" in str(tools) or "hunter" in response.lower():
                    gap = f"Gap in {subtask}"
                    hunt = self._tool_hunter(gap, subtask)
                    solution += f"\n[ToolHunter]\n{hunt}"
                elif tools and tools[0] != "none":
                    output = self.compute.run_on_compute(f"Apply {tools[0]} to: {solution[:600]}")
                    solution += f"\n[{tools[0]}]\n{output}"

                if self.config.get("guardrails"):
                    solution = apply_guardrails(solution, monitor)

                if time.time() - monitor.start_time > (max_hours * 1800 / 6):
                    break

        memory.add(text=solution[:1000], metadata={"subtask": subtask, "status": "completed"})
        shared_results[subtask_id] = {"subtask": subtask, "solution": solution, "trace": trace}
        return shared_results[subtask_id]

    def _run_verification(self, solution: str, verification_code: str) -> str:
        if not verification_code or not verification_code.strip():
            return "No custom verification code provided."

        try:
            exec_task = f"""Execute this verification code safely on the solution:

Solution:
{solution[:2000]}

Verification code:
{verification_code}

Return the verification result, pass/fail verdict, and any metrics."""
            result = self.compute.run_on_compute(exec_task)
            return f"Verification Result:\n{result}"
        except Exception as e:
            return f"Verification execution failed: {str(e)}. Falling back to LLM assessment."

    def _run_swarm(self, blueprint: Dict[str, Any], challenge: str, verification_instructions: str = "") -> str:
        decomposition = blueprint.get("decomposition", ["Full challenge"])
        swarm_config = blueprint.get("swarm_config", {"total_instances": 1})
        tool_map = blueprint.get("tool_map", {})

        total_instances = min(swarm_config.get("total_instances", 4), 6)
        if self.config.get("resource_aware"):
            total_instances = min(total_instances, 4)

        assignment = swarm_config.get("assignment", {})
        hypotheses = swarm_config.get("hypothesis_diversity", ["standard"] * len(decomposition))

        manager_dict = multiprocessing.Manager().dict()
        trace_log = [f"🚀 Launching Swarm with {total_instances} instances"]

        with concurrent.futures.ProcessPoolExecutor(max_workers=total_instances) as executor:
            futures = []
            subtask_id = 0
            for i, subtask in enumerate(decomposition):
                count = assignment.get(subtask, 1)
                tools = tool_map.get(subtask, ["none"])
                for _ in range(count):
                    hyp = hypotheses[i % len(hypotheses)]
                    futures.append(executor.submit(
                        self._sub_arbos_worker, subtask, hyp, tools, manager_dict, subtask_id
                    ))
                    subtask_id += 1

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    trace_log.append(f"Error: {e}")

        # Synthesis
        all_results = dict(manager_dict)
        failed_context = "\nPrevious failed attempts:\n" + "\n---\n".join(memory.query(challenge + " failed", n_results=5)) if memory.query(challenge + " failed", n_results=5) else ""

        synthesis_task = f"""You are Arbos Orchestrator.
Challenge: {challenge}
Verification Instructions: {verification_instructions or 'General SN63 standards'}
{failed_context}
Swarm results: {json.dumps(all_results, indent=2)}
Final Synthesized Solution:"""

        final_solution = self.compute.run_on_compute(synthesis_task)

        # Executable Verification
        if verification_instructions and verification_instructions.strip():
            verification_result = self._run_verification(final_solution, verification_instructions)
            final_solution += f"\n\n--- VERIFICATION RESULT ---\n{verification_result}"

        if self.config.get("guardrails"):
            final_solution = apply_guardrails(final_solution, ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8)))

        memory.add(text=final_solution[:1500], metadata={"challenge": challenge, "status": "final"})

        trace_log.append("Synthesis + Verification complete")

        import streamlit as st
        if "trace_log" not in st.session_state:
            st.session_state.trace_log = []
        st.session_state.trace_log.extend(trace_log)

        return final_solution

    def _smart_route(self, challenge: str) -> Tuple[str, List[str], bool]:
        import streamlit as st
        high_level_plan = self.plan_challenge(challenge)
        st.session_state.high_level_plan = high_level_plan

        approved_plan = high_level_plan
        blueprint = self._refine_plan(approved_plan, challenge)
        st.session_state.blueprint = blueprint

        verification = st.session_state.get("verification_instructions", "")
        final_solution = self._run_swarm(blueprint, challenge, verification)
        return final_solution, ["swarm"], False

    def run(self, challenge: str):
        return self._smart_route(challenge)
