# agents/arbos_manager.py
# FINAL VERSION - Auto-reloop with max_loops toggle + Final mandatory review

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
        self._setup_real_arbos()
        print("✅ REAL Arbos + Long-term Memory + Reflection Loop loaded")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "reflection": 4,
            "hyper_planning": True,
            "exploration": True,
            "resource_aware": True,
            "guardrails": True,
            "miner_review_after_loop": False,
            "max_loops": 4,                    # New toggle
            "miner_review_final": True
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("reflection:"):
                        config["reflection"] = int(line.split(":")[1].strip())
                    elif line.startswith("hyper_planning:"):
                        config["hyper_planning"] = "true" in line
                    elif line.startswith("exploration:"):
                        config["exploration"] = "true" in line
                    elif line.startswith("resource_aware:"):
                        config["resource_aware"] = "true" in line
                    elif line.startswith("guardrails:"):
                        config["guardrails"] = "true" in line
                    elif line.startswith("miner_review_after_loop:"):
                        config["miner_review_after_loop"] = "true" in line
                    elif line.startswith("max_loops:"):
                        config["max_loops"] = int(line.split(":")[1].strip())
                    elif line.startswith("miner_review_final:"):
                        config["miner_review_final"] = "true" in line
        except Exception:
            pass
        return config

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str], bool]:
        from agents.tool_study import tool_study
        import streamlit as st

        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = approved_plan[:1500] if approved_plan else ""
        trace_log = []

        past_knowledge = memory.query(challenge, n_results=4)
        if past_knowledge:
            cumulative_context += "\n\nRelevant past knowledge:\n" + "\n---\n".join(past_knowledge)

        program_path = Path("program.md")
        if not program_path.exists():
            program_path.write_text(f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Approved Plan\n{approved_plan}\n\n")

        monitor = ResourceMonitor(max_hours=3.8)
        elapsed = monitor.elapsed_hours()
        remaining_hours = 3.8 - elapsed
        reflection_depth = 3 if remaining_hours > 2.0 else 2 if remaining_hours > 1.0 else 1

        trace_log.append(f"Time remaining: {remaining_hours:.2f}h | Reflection depth: {reflection_depth}")

        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_relevant_profile(next_tool, query=cumulative_context + " " + last_output)
            try:
                task = f"""You are Arbos...

Previous: {last_output}
Goal: {challenge}
Next tool: {next_tool}
Time left: {remaining_hours:.2f}h

Tool Profile: {tool_profile}

Mimic intelligently. Consider cost.

Reply exactly:
Prompt: [prompt]
Recommended Compute: [chutes/targon/celium/local]"""

                response = self.compute.run_on_compute(task)
                prompt_part = response.split("Prompt:")[-1] if "Prompt:" in response else response
                compute_override = response.split("Recommended Compute:")[-1].strip().lower() if "Recommended Compute:" in response else None

                trace_log.append(f"[{next_tool}] Profile used | Compute: {compute_override or 'default'}")
                return {"prompt": prompt_part.strip(), "compute_override": compute_override}
            except Exception:
                trace_log.append(f"[{next_tool}] Reflection fallback")
                return {"prompt": f"Continue with previous findings using {next_tool}.", "compute_override": None}

        last_output = ""
        max_loops = self.config.get("max_loops", 4)

        for loop in range(max_loops):
            trace_log.append(f"--- Starting Loop {loop+1}/{max_loops} ---")

            tool_sequence = ["AI-Researcher", "AutoResearch", "GPD", "ScienceClaw"]
            for tool_name in tool_sequence:
                decide_task = f"""Should we use {tool_name} now? Context: {cumulative_context[:600]}"""
                decision = self.compute.run_on_compute(decide_task)

                if "YES" in decision.upper():
                    redesign = reflect_and_redesign(last_output, tool_name)
                    result = self.compute.run_on_compute(redesign["prompt"], override_compute=redesign.get("compute_override"))
                    output = result

                    results.append(f"[{tool_name}]\n{output}")
                    used_tools.append(tool_name)
                    cumulative_context += f"\n\n[{tool_name} Output]\n{output}"
                    last_output = output

            # Real ScienceClaw at end of each loop
            if any(k in lower for k in ["analyze", "experiment", "data", "science", "conclude"]):
                redesign = reflect_and_redesign(last_output, "ScienceClaw")
                result = run_scienceclaw(task=redesign["prompt"])
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[ScienceClaw - REAL]\n{output}")
                used_tools.append("ScienceClaw")
                cumulative_context += f"\n\n[ScienceClaw REAL]\n{output}"

            memory.add(text="\n\n".join(results), metadata={"loop": loop+1})

            # If miner wants review after every loop, stop after this one
            if self.config.get("miner_review_after_loop", False):
                break

        st.session_state.trace_log = trace_log
        return "\n\n".join(results), used_tools, self.config.get("miner_review_after_loop", False)

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used} | Max loops used: {self.config.get('max_loops', 4)}")
        return final_output, should_reloop
