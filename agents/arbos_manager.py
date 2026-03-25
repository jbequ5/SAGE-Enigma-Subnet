# agents/arbos_manager.py
# FINAL VERSION - Full GOAL.md context + auto-reloop + max_loops + final review

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
        print("✅ REAL Arbos + Full GOAL.md Context + Auto-ReLoop loaded")

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
                    line = line.strip().lower()
                    if line.startswith("reflection:"):
                        config["reflection"] = int(line.split(":")[1].strip())
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
                    elif line.startswith("chutes:"):
                        config["chutes"] = "true" in line
                    elif line.startswith("targon:"):
                        config["targon"] = "true" in line
                    elif line.startswith("celium:"):
                        config["celium"] = "true" in line
                    elif line.startswith("chutes_llm:"):
                        config["chutes_llm"] = line.split(":")[1].strip()
        except Exception:
            pass
        return config

    def _load_extra_context(self) -> str:
        """Load everything in GOAL.md after the toggles as strategic context"""
        try:
            with open(self.goal_file, "r") as f:
                content = f.read()

            # Split at the last toggle line and take everything after it
            lines = content.splitlines()
            context_lines = []
            in_context = False

            for line in lines:
                stripped = line.strip().lower()
                if stripped.startswith(("miner_review_after_loop:", "max_loops:", "miner_review_final:",
                                        "chutes:", "targon:", "celium:", "chutes_llm:")):
                    in_context = True
                    continue
                if in_context and line.strip() and not line.strip().startswith("#"):
                    context_lines.append(line.strip())

            return "\n".join(context_lines) if context_lines else ""
        except Exception:
            return ""

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str], bool]:
        from agents.tool_study import tool_study
        import streamlit as st

        full_context = f"{challenge}\n\n{approved_plan}\n\n{self.extra_context}".strip()

        results = []
        used_tools = []
        cumulative_context = full_context[:2000]
        trace_log = []

        # Long-term memory
        past = memory.query(challenge, n_results=4)
        if past:
            cumulative_context += "\n\nPast knowledge:\n" + "\n---\n".join(past)

        monitor = ResourceMonitor(max_hours=3.8)
        remaining_hours = 3.8 - monitor.elapsed_hours()
        reflection_depth = 3 if remaining_hours > 2.0 else 2 if remaining_hours > 1.0 else 1

        trace_log.append(f"Time remaining: {remaining_hours:.2f}h | Depth: {reflection_depth} | Extra context length: {len(self.extra_context)}")

        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_relevant_profile(next_tool, query=cumulative_context + " " + last_output)
            try:
                task = f"""You are Arbos.

Goal: {challenge}
Extra Strategy from Miner (GOAL.md): {self.extra_context}

Previous output: {last_output}
Next tool: {next_tool}
Time left: {remaining_hours:.2f}h

Tool Profile: {tool_profile}

Mimic the tool intelligently and align with the miner's strategy.

Reply exactly:
Prompt: [full prompt]
Recommended Compute: [chutes/targon/celium/local]"""

                response = self.compute.run_on_compute(task)
                prompt_part = response.split("Prompt:")[-1] if "Prompt:" in response else response
                compute_override = response.split("Recommended Compute:")[-1].strip().lower() if "Recommended Compute:" in response else None

                trace_log.append(f"[{next_tool}] Used context | Compute: {compute_override or 'default'}")
                return {"prompt": prompt_part.strip(), "compute_override": compute_override}
            except Exception:
                trace_log.append(f"[{next_tool}] Fallback")
                return {"prompt": f"Continue with previous findings using {next_tool}.", "compute_override": None}

        last_output = ""
        max_loops = self.config.get("max_loops", 4)

        for loop in range(max_loops):
            trace_log.append(f"--- Loop {loop+1}/{max_loops} ---")

            for tool_name in ["AI-Researcher", "AutoResearch", "GPD", "ScienceClaw"]:
                decide = self.compute.run_on_compute(f"Should we use {tool_name} now? Context: {cumulative_context[:600]}")
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

        st.session_state.trace_log = trace_log
        return "\n\n".join(results), used_tools, self.config.get("miner_review_after_loop", False)

    def run(self, challenge: str):
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output, should_reloop
