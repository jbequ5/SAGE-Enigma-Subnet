# agents/arbos_manager.py
# FINAL CLEAN OPERATIONAL VERSION - Reflection after every tool + Long-term memory + program.md

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

# Core imports
from agents.memory import memory

# Supporting tools only (no old run_xxx wrappers)
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
            "guardrails": True
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
        except Exception:
            pass
        return config

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str]]:
        """
        FINAL CLEAN VERSION - Mimic first three tools + REAL ScienceClaw at the end
        """
        from agents.tool_study import tool_study

        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = approved_plan[:1500] if approved_plan else ""

        # Long-term memory
        past_knowledge = memory.query(challenge, n_results=4)
        if past_knowledge:
            cumulative_context += "\n\nRelevant past knowledge from previous runs:\n" + "\n---\n".join(past_knowledge)

        program_path = Path("program.md")
        if not program_path.exists():
            program_path.write_text(f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Approved Plan\n{approved_plan}\n\n")

        # Reflection helper
        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            tool_profile = tool_study.load_profile(next_tool)
            try:
                task = f"""You are Arbos, a highly intelligent conductor.

Previous tool output: {last_output}
Overall goal: {challenge}
Next tool: {next_tool}

Tool Profile:
{tool_profile}

Using this profile, mimic the real {next_tool} tool as closely and intelligently as possible.
Create a high-quality prompt that behaves like the real tool would.

Reply in this exact format:
Prompt: [the full prompt to send]
Recommended Compute: [chutes/targon/celium/local]"""

                result = self.compute.run_on_compute(task)
                response = result

                prompt_part = response.split("Prompt:")[-1] if "Prompt:" in response else response
                compute_override = None
                if "Recommended Compute:" in response:
                    compute_override = response.split("Recommended Compute:")[-1].strip().lower()

                return {"prompt": prompt_part.strip(), "compute_override": compute_override}
            except Exception:
                return {"prompt": f"Continue with previous findings using {next_tool} style.", "compute_override": None}

        last_output = ""

        # === Mimic the first three tools ===
        mimic_tools = ["AI-Researcher", "AutoResearch", "GPD"]

        for tool_name in mimic_tools:
            decide_task = f"""Challenge: {challenge}
Cumulative context so far: {cumulative_context[:800]}

Should we use the {tool_name} tool at this stage?
Reply with only YES or NO, followed by a very short reason."""

            decision = self.compute.run_on_compute(decide_task)

            if "YES" in decision.upper():
                redesign = reflect_and_redesign(last_output, tool_name)
                task = redesign["prompt"]
                compute_override = redesign.get("compute_override")

                result = self.compute.run_on_compute(task, override_compute=compute_override)
                output = result

                results.append(f"[{tool_name}]\n{output}")
                used_tools.append(tool_name)
                cumulative_context += f"\n\n[{tool_name} Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + redesign["prompt"]
                last_output = output

        # === REAL ScienceClaw at the end of every loop ===
        if any(k in lower for k in ["analyze", "experiment", "data", "science", "conclude"]):
            try:
                redesign = reflect_and_redesign(last_output, "ScienceClaw")
                task = redesign["prompt"]

                result = run_scienceclaw(task=task)
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[ScienceClaw - REAL]\n{output}")
                used_tools.append("ScienceClaw")
                cumulative_context += f"\n\n[ScienceClaw REAL Output]\n{output}"
            except Exception as e:
                results.append(f"[ScienceClaw Error] {str(e)}")

        # Save to long-term memory
        if results:
            memory.add(
                text="\n\n".join(results),
                metadata={"challenge": challenge, "tools_used": ",".join(used_tools)}
            )

        if not results:
            results.append("No specialized tool triggered. Using default Arbos reasoning.")
            used_tools.append("Arbos Core")

        return "\n\n".join(results), used_tools
        
    def run(self, challenge: str):
        """Main entry point"""
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output
