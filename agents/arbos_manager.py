# agents/arbos_manager.py
# PRIMARY SOLVER VERSION - Arbos-centric with intelligent planning, dynamic swarm, 
# ToolHunter, dynamic compute limits, and enhanced re-loop memory

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
from agents.tools.exploration import explore_novel_variant
from agents.tools.tool_hunter import tool_hunter


class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()
        print("✅ Arbos Primary Solver Mode loaded")
        print(f"   → Dynamic compute limit: {self.config.get('max_compute_hours')} hours")
        print("   → Enhanced re-loop memory + Planning + Swarm + ToolHunter enabled")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "reflection": 4,
            "exploration": True,
            "resource_aware": True,
            "guardrails": True,
            "miner_review_after_loop": False,
            "max_loops": 5,
            "miner_review_final": True,
            "chutes": True,
            "chutes_llm": "mixtral",
            "max_compute_hours": 3.8,
            "max_compute_minutes": 228
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    stripped = line.strip().lower()
                    if stripped.startswith("reflection:"):
                        config["reflection"] = int(line.split(":")[1].strip())
                    elif stripped.startswith("exploration:"):
                        config["exploration"] = "true" in stripped
                    elif stripped.startswith("resource_aware:"):
                        config["resource_aware"] = "true" in stripped
                    elif stripped.startswith("guardrails:"):
                        config["guardrails"] = "true" in stripped
                    elif stripped.startswith("miner_review_after_loop:"):
                        config["miner_review_after_loop"] = "true" in stripped
                    elif stripped.startswith("max_loops:"):
                        config["max_loops"] = int(line.split(":")[1].strip())
                    elif stripped.startswith("miner_review_final:"):
                        config["miner_review_final"] = "true" in stripped
                    elif stripped.startswith("chutes:"):
                        config["chutes"] = "true" in stripped
                    elif stripped.startswith("chutes_llm:"):
                        config["chutes_llm"] = line.split(":")[1].strip()
                    elif stripped.startswith("max_compute_hours:"):
                        config["max_compute_hours"] = float(line.split(":")[1].strip())
                    elif stripped.startswith("max_compute_minutes:"):
                        config["max_compute_minutes"] = int(line.split(":")[1].strip())
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

    # ===================================================================
    # META PLANNING ARBOS
    # ===================================================================
    def plan_challenge(self, challenge: str) -> Dict[str, Any]:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours)
        remaining_hours = max_hours - monitor.elapsed_hours()

        full_context = f"""CHALLENGE: {challenge}

MINER STRATEGY (HIGH PRIORITY):
{self.extra_context}

Time available: {remaining_hours:.2f}h"""

        past = memory.query(challenge, n_results=6)
        if past:
            full_context += "\n\nPast attempts and critiques:\n" + "\n---\n".join(past)

        planning_task = f"""You are Planning Arbos, a meta-planner specialized for Bittensor SN63 challenges.

{full_context}

Create a high-level executable plan for an extremely hard problem.
Strictly follow miner strategy. Bias toward novelty, verifier potential, and realistic compute use.

Output EXACTLY this JSON (no extra text):
{{
  "high_level_goals": "one sentence summary",
  "risks_and_mitigations": ["risk1", "risk2", ...],
  "rough_decomposition": ["subtask1 description", "subtask2 description", ...],
  "suggested_swarm_size": 4,
  "high_level_tool_hints": {{"subtask1": ["ScienceClaw"], "subtask2": ["ToolHunter"]}},
  "compute_ballpark_minutes": 210,
  "quality_gate_targets": {{"novelty": 8.5, "verifier": 9.0, "alignment": 9.5, "completeness": 9.0}}
}}

Critique your own plan for SN63 optimality before outputting."""

        response = self.compute.run_on_compute(planning_task)
        return self._parse_json(response)

    # ===================================================================
    # PLAN REFINEMENT (Orchestrator Arbos)
    # ===================================================================
    def _refine_plan(self, approved_plan: Dict[str, Any], challenge: str) -> Dict[str, Any]:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours)
        remaining_hours = max_hours - monitor.elapsed_hours()

        refinement_task = f"""You are Arbos, the primary orchestrator.

CHALLENGE: {challenge}
APPROVED HIGH-LEVEL PLAN:
{json.dumps(approved_plan, indent=2)}

MINER STRATEGY:
{self.extra_context}

Time left: {remaining_hours:.2f}h

Refine into precise executable blueprint.

Output EXACTLY this JSON:
{{
  "decomposition": ["detailed subtask1", "detailed subtask2", ...],
  "swarm_config": {{
    "total_instances": 5,
    "assignment": {{"subtask1": 1, "subtask2": 2, ...}},
    "hypothesis_diversity": ["classical baseline", "quantum VQE", "bio-inspired", ...]
  }},
  "tool_map": {{"subtask1": ["ScienceClaw"], "subtask2": ["ToolHunter"], ...}},
  "compute_projection_minutes": 195,
  "risk_flags": ["high_simulation_load"],
  "quality_gate_targets": {{"novelty": 9.0, "verifier": 9.5, ...}},
  "early_abort_triggers": ["if any subtask > 40min"]
}}

Project realistic compute time. Propose conservative fallback if needed."""

        response = self.compute.run_on_compute(refinement_task)
        return self._parse_json(response)

    def _parse_json(self, raw_response: str) -> Dict[str, Any]:
        try:
            start = raw_response.find("{")
            end = raw_response.rfind("}") + 1
            json_str = raw_response[start:end]
            return json.loads(json_str)
        except Exception:
            return {
                "decomposition": ["Fallback: process full challenge as one subtask"],
                "swarm_config": {"total_instances": 1, "assignment": {}},
                "tool_map": {},
                "compute_projection_minutes": 210,
                "risk_flags": ["JSON parse fallback"]
            }

    # ===================================================================
    # TOOL HUNTER
    # ===================================================================
    def _tool_hunter(self, gap_description: str, subtask: str) -> str:
        result = tool_hunter.hunt_and_integrate(
            gap_description=gap_description,
            subtask=subtask,
            challenge_context=f"SN63 challenge: {subtask}"
        )
        if result["status"] == "success":
            return f"ToolHunter SUCCESS: {result.get('tool_name')} | Integration ready"
        else:
            return f"ToolHunter MANUAL REQUIRED: {result.get('miner_recommendation', result.get('reason', 'No tool found'))}"

    # ===================================================================
    # SUB-ARBOS WORKER
    # ===================================================================
    def _sub_arbos_worker(self, subtask: str, hypothesis: str, tools: List[str],
                          shared_results: dict, subtask_id: int) -> dict:
        max_hours = self.config.get("max_compute_hours", 3.8)
        monitor = ResourceMonitor(max_hours=max_hours / 3)
        start_time = time.time()

        solution = f"Subtask: {subtask}\nHypothesis: {hypothesis}"
        used_tools = []
        trace = [f"Sub-Arbos {subtask_id} started"]

        for loop in range(3):
            reflect_task = f"""You are a focused sub-Arbos.

Subtask: {subtask}
Hypothesis: {hypothesis}
Current: {solution[:800]}

Critique novelty, verifier potential, alignment with miner strategy.
Decide: Improve / Call Tool / Finalize"""

            response = self.compute.run_on_compute(reflect_task)
            trace.append(f"Loop {loop+1}: {response[:150]}...")

            if "Finalize" in response or "final" in response.lower():
                break

            if "ToolHunter" in tools or "hunter" in response.lower():
                gap = "Specialized tool needed for this subtask gap"
                hunt_result = self._tool_hunter(gap, subtask)
                solution += f"\n\n[ToolHunter]\n{hunt_result}"
                used_tools.append("ToolHunter")
            elif tools and tools[0] != "none":
                tool_name = tools[0]
                output = self.compute.run_on_compute(f"Apply {tool_name} style to: {solution[:600]}")
                solution += f"\n\n[{tool_name}]\n{output}"
                used_tools.append(tool_name)
            else:
                solution = response

            if time.time() - start_time > (max_hours * 1800 / 6):
                trace.append("Subtask time cap reached")
                break

        # Store subtask result in memory
        memory.add(
            text=f"Subtask result: {solution[:800]}...",
            metadata={"subtask": subtask, "hypothesis": hypothesis, "status": "completed", "subtask_id": subtask_id}
        )

        shared_results[subtask_id] = {
            "subtask": subtask,
            "hypothesis": hypothesis,
            "solution": solution,
            "tools_used": used_tools,
            "trace": trace
        }
        return shared_results[subtask_id]

    # ===================================================================
    # DYNAMIC SWARM + SYNTHESIS + STRONGER RE-LOOP MEMORY
    # ===================================================================
    def _run_swarm(self, blueprint: Dict[str, Any], challenge: str) -> str:
        decomposition = blueprint.get("decomposition", ["Full challenge"])
        swarm_config = blueprint.get("swarm_config", {"total_instances": 1, "assignment": {}})
        tool_map = blueprint.get("tool_map", {})

        total_instances = min(swarm_config.get("total_instances", 4), 6)
        assignment = swarm_config.get("assignment", {})
        hypotheses = swarm_config.get("hypothesis_diversity", ["standard approach"] * len(decomposition))

        trace_log = ["🚀 Launching Dynamic Swarm...", f"Instances: {total_instances}"]

        manager_dict = multiprocessing.Manager().dict()

        with concurrent.futures.ProcessPoolExecutor(max_workers=total_instances) as executor:
            futures = []
            subtask_id = 0
            for i, subtask in enumerate(decomposition):
                assigned_count = assignment.get(subtask, 1)
                tools_for_subtask = tool_map.get(subtask, ["none"])
                for _ in range(assigned_count):
                    hyp = hypotheses[i % len(hypotheses)] if hypotheses else "standard"
                    futures.append(
                        executor.submit(self._sub_arbos_worker, subtask, hyp, tools_for_subtask, manager_dict, subtask_id)
                    )
                    subtask_id += 1

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    trace_log.append(f"✓ Subtask completed: {result.get('subtask', '')[:80]}...")
                except Exception as e:
                    trace_log.append(f"✗ Subtask error: {e}")

        # Synthesis with enhanced re-loop memory
        all_results = dict(manager_dict)
        failed_attempts = memory.query(challenge + " failed", n_results=5)
        failed_context = "\nPrevious failed attempts and critiques:\n" + "\n---\n".join(failed_attempts) if failed_attempts else ""

        synthesis_task = f"""You are Arbos Orchestrator. Synthesize the swarm results into one coherent, high-novelty, verifier-strong solution.

Challenge: {challenge}
{failed_context}

Swarm results:
{json.dumps(all_results, indent=2)}

Follow miner strategy from killer_base.md. Learn from previous failures.

Final Synthesized Solution:"""

        final_solution = self.compute.run_on_compute(synthesis_task)

        # Store final attempt for future re-loops
        memory.add(
            text=final_solution[:1500],
            metadata={"challenge": challenge, "status": "final_attempt", "timestamp": time.time()}
        )

        trace_log.append("Swarm synthesis complete")

        import streamlit as st
        if "trace_log" not in st.session_state:
            st.session_state.trace_log = []
        st.session_state.trace_log.extend(trace_log)

        return final_solution

    # ===================================================================
    # ORCHESTRATOR
    # ===================================================================
    def _smart_route(self, challenge: str) -> Tuple[str, List[str], bool]:
        import streamlit as st

        trace_log = ["🚀 Starting Arbos Orchestrator"]

        trace_log.append("→ Running Intelligent Planning Arbos...")
        high_level_plan = self.plan_challenge(challenge)

        st.session_state.high_level_plan = high_level_plan
        st.session_state.trace_log = trace_log

        approved_plan = high_level_plan   # Streamlit will override with real approval in full flow

        trace_log.append("→ Running Orchestrator Arbos Refinement...")
        blueprint = self._refine_plan(approved_plan, challenge)

        st.session_state.blueprint = blueprint
        st.session_state.trace_log = trace_log

        trace_log.append("→ Launching parallel Sub-Arbos swarm with per-subtask ToolHunter...")
        final_solution = self._run_swarm(blueprint, challenge)

        tools_used = ["swarm_various"]
        should_reloop = self.config.get("miner_review_after_loop", False)

        st.session_state.trace_log = trace_log
        return final_solution, tools_used, should_reloop

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos Orchestrator for: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=self.config.get("max_compute_hours", 3.8))

        final_solution, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(final_solution, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        # Store final output
        memory.add(
            text=final_output[:1000],
            metadata={"challenge": challenge, "status": "final", "compute_used": monitor.elapsed_hours()}
        )

        print(f"✅ Completed.")
        return final_output, should_reloop
