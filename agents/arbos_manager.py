# agents/arbos_manager.py
# FINAL STRENGTHENED VERSION WITH ADAPTIVE QUALITY GATE + SMART RE-LOOP

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

from agents.memory import memory

from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails
from agents.tools.exploration import explore_novel_variant

class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self.extra_context = self._load_extra_context()
        self._setup_real_arbos()
        print("✅ Arbos with Adaptive Quality Gate + Smart Re-Loop loaded")

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
            "max_loops": 4,
            "miner_review_final": True,
            "chutes": True,
            "targon": False,
            "celium": False,
            "chutes_llm": "mixtral"
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
                    elif stripped.startswith("targon:"):
                        config["targon"] = "true" in stripped
                    elif stripped.startswith("celium:"):
                        config["celium"] = "true" in stripped
                    elif stripped.startswith("chutes_llm:"):
                        config["chutes_llm"] = line.split(":")[1].strip()
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

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str], bool]:
        from agents.tool_study import tool_study
        import streamlit as st

        full_context = f"""GOAL: {challenge}

MINER STRATEGY (HIGH PRIORITY - FOLLOW CLOSELY):
{self.extra_context}

APPROVED PLAN:
{approved_plan}""".strip()

        results = []
        used_tools = []
        cumulative_context = full_context
        trace_log = []

        past = memory.query(challenge, n_results=6)
        if past:
            cumulative_context += "\n\nPrevious loop knowledge:\n" + "\n---\n".join(past)

        monitor = ResourceMonitor(max_hours=3.8)
        remaining_hours = 3.8 - monitor.elapsed_hours()
        reflection_depth = 3 if remaining_hours > 2.0 else 2 if remaining_hours > 1.0 else 1

        trace_log.append(f"Time left: {remaining_hours:.2f}h | Depth: {reflection_depth}")

        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_relevant_profile(next_tool, query=cumulative_context)
            few_shot = {
                "GPD": "Real GPD breaks problems into deep theory → numerical validation → experimental implications.",
                "AutoResearch": "Real AutoResearch writes, executes, debugs, and iterates code until the goal is met.",
                "AI-Researcher": "Real AI-Researcher finds cross-domain papers and synthesizes novel connections.",
                "ScienceClaw": "Real ScienceClaw performs rigorous scientific analysis and proposes concrete experiments."
            }

            try:
                task = f"""You are Arbos.

GOAL: {challenge}
MINER STRATEGY (FOLLOW VERY CLOSELY):
{self.extra_context}

Previous output: {last_output}
Next tool: {next_tool}
Time left: {remaining_hours:.2f}h

How the real {next_tool} behaves:
{few_shot.get(next_tool, "Act with high intelligence.")}

Tool Profile: {tool_profile}

Think step-by-step and produce output that strongly aligns with miner strategy.

Reply exactly:
Prompt: [full prompt]
Recommended Compute: [chutes/targon/celium/local]"""

                response = self.compute.run_on_compute(task)
                prompt_part = response.split("Prompt:")[-1] if "Prompt:" in response else response
                compute_override = response.split("Recommended Compute:")[-1].strip().lower() if "Recommended Compute:" in response else None

                trace_log.append(f"[{next_tool}] Strong mimic | Compute: {compute_override or 'default'}")
                return {"prompt": prompt_part.strip(), "compute_override": compute_override}
            except Exception:
                trace_log.append(f"[{next_tool}] Fallback")
                return {"prompt": f"Continue with previous findings using {next_tool}.", "compute_override": None}

        last_output = ""
        max_loops = self.config.get("max_loops", 4)

        for loop in range(max_loops):
            trace_log.append(f"--- Loop {loop+1}/{max_loops} ---")

            for tool_name in ["AI-Researcher", "AutoResearch", "GPD", "ScienceClaw"]:
                decide = self.compute.run_on_compute(f"Given miner strategy, should we use {tool_name} now?")
                if "YES" in decide.upper():
                    redesign = reflect_and_redesign(last_output, tool_name)
                    result = self.compute.run_on_compute(redesign["prompt"], override_compute=redesign.get("compute_override"))
                    output = result

                    results.append(f"[{tool_name}]\n{output}")
                    used_tools.append(tool_name)
                    cumulative_context += f"\n\n[{tool_name}]\n{output}"
                    last_output = output

            # Real ScienceClaw
            if any(k in lower for k in ["analyze", "experiment", "data", "science", "conclude"]):
                redesign = reflect_and_redesign(last_output, "ScienceClaw")
                result = run_scienceclaw(task=redesign["prompt"])
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[ScienceClaw - REAL]\n{output}")
                used_tools.append("ScienceClaw")
                cumulative_context += f"\n\n[ScienceClaw REAL]\n{output}"

            memory.add(text="\n\n".join(results), metadata={"loop": loop+1})

            if self.config.get("miner_review_after_loop", False):
                break

        # === ADAPTIVE QUALITY GATE ===
        critique_task = f"""Evaluate the current solution:

Goal: {challenge}
Miner Strategy: {self.extra_context}

Current Solution:
{last_output}

Score on a scale of 1-10 for:
- Novelty
- Verifier Score Potential
- Alignment with Miner Strategy
- Completeness
- Feasibility under remaining time

Then decide:
Should we do another loop? Reply with:
Score: [numbers]
Decision: [YES/NO - Re-loop or Finalize]
Reason: [short reason]"""

        critique = self.compute.run_on_compute(critique_task)
        trace_log.append(f"Quality Gate Critique: {critique[:300]}...")

        should_reloop = "YES" in critique.upper() and not self.config.get("miner_review_after_loop", False)

        st.session_state.trace_log = trace_log
        return "\n\n".join(results), used_tools, should_reloop

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used} | Re-loop decision: {should_reloop}")
        return final_output, should_reloop
