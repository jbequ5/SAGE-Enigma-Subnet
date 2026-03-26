# agents/arbos_manager.py
# COMPLETE FINAL VERSION

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


class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
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
                    if key == "miner_review_after_loop":
                        config["miner_review_after_loop"] = "true" in value.lower()
                    elif key == "max_loops":
                        config["max_loops"] = int(value)
                    elif key == "miner_review_final":
                        config["miner_review_final"] = "true" in value.lower()
                    elif key == "chutes":
                        config["chutes"] = "true" in value.lower()
                    elif key == "chutes_llm":
                        config["chutes_llm"] = value
                    elif key == "max_compute_hours":
                        config["max_compute_hours"] = float(value)
                    elif key == "resource_aware":
                        config["resource_aware"] = "true" in value.lower()
                    elif key == "guardrails":
                        config["guardrails"] = "true" in value.lower()
                    elif key == "toolhunter_escalation":
                        config["toolhunter_escalation"] = "true" in value.lower()
                    elif key == "manual_tool_installs_allowed":
                        config["manual_tool_installs_allowed"] = "true" in value.lower()
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

    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str], shared_results: dict, subtask_id: int) -> dict:
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

    def _run_swarm(self, blueprint: Dict, challenge: str, verification_instructions: str = "") -> str:
        decomposition = blueprint.get("decomposition", ["Full challenge"])
        swarm_config = blueprint.get("swarm_config", {"total_instances": 1})
        tool_map = blueprint.get("tool_map", {})

        total_instances = min(swarm_config.get("total_instances", 4), 6)
        assignment = swarm_config.get("assignment", {})
        hypotheses = swarm_config.get("hypothesis_diversity", ["standard"] * len(decomposition))

        manager_dict = multiprocessing.Manager().dict()
        trace_log = ["Swarm started"]

        with concurrent.futures.ProcessPoolExecutor(max_workers=total_instances) as executor:
            futures = []
            subtask_id = 0
            for i, subtask in enumerate(decomposition):
                count = assignment.get(subtask, 1)
                tools = tool_map.get(subtask, ["none"])
                for _ in range(count):
                    hyp = hypotheses[i % len(hypotheses)]
                    futures.append(executor.submit(self._sub_arbos_worker, subtask, hyp, tools, manager_dict, subtask_id))
                    subtask_id += 1

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    trace_log.append(f"Error: {e}")

        all_results = dict(manager_dict)
        synthesis_task = f"""Synthesize results.
Challenge: {challenge}
Verification: {verification_instructions or 'General SN63 standards'}
Results: {json.dumps(all_results, indent=2)}
Final Solution:"""
        final_solution = self.compute.run_on_compute(synthesis_task)

        if self.config.get("guardrails"):
            final_solution = apply_guardrails(final_solution, ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8)))

        memory.add(text=final_solution[:1500], metadata={"challenge": challenge, "status": "final"})

        return final_solution

    def _smart_route(self, challenge: str) -> Tuple[str, List[str], bool]:
        import streamlit as st
        high_level_plan = self.plan_challenge(challenge)
        st.session_state.high_level_plan = high_level_plan

        approved_plan = high_level_plan
        blueprint = self._refine_plan(approved_plan, challenge)
        st.session_state.blueprint = blueprint

        final_solution = self._run_swarm(blueprint, challenge, st.session_state.get("verification_instructions", ""))
        return final_solution, ["swarm"], False

    def run(self, challenge: str):
        return self._smart_route(challenge)
