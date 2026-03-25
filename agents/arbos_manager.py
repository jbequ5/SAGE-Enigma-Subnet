# agents/arbos_manager.py
# FINAL OPERATIONAL VERSION - Reflection after every tool + Long-term memory + program.md

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

# Core imports
from agents.memory import memory

# Tool imports (subfolder structure)
from agents.tools.hyperagent import run_hyperagent
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.autoresearch import run_autoresearch
from agents.tools.get_physics_done import run_gpd
from agents.tools.scienceclaw import run_scienceclaw

# Supporting tools
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
        FINAL REALISTIC _smart_route
        - Uses the actual tool wrappers
        - Reflection + prompt redesign after every tool
        - Long-term memory + program.md
        """
        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = approved_plan[:1500] if approved_plan else ""

        # Long-term memory
        past_knowledge = memory.query(challenge, n_results=4)
        if past_knowledge:
            cumulative_context += "\n\nRelevant past knowledge:\n" + "\n---\n".join(past_knowledge)

        program_path = Path("program.md")
        if not program_path.exists():
            program_path.write_text(f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Approved Plan\n{approved_plan}\n\n")

        # Reflection helper
        def reflect_and_redesign(last_output: str, next_tool: str) -> dict:
            try:
                task = f"""Previous tool output: {last_output}
Overall goal: {challenge}
Next tool: {next_tool}

Reconstruct into a specific prompt for the next tool.
Reply in this format:
Prompt: [full prompt]
Recommended Compute: [chutes/targon/celium/local]"""
                result = run_hyperagent(task=task, parallel_tasks=3)
                response = result.get("output", "")

                prompt_part = response.split("Prompt:")[-1]
                compute_override = None
                if "Recommended Compute:" in prompt_part:
                    prompt = prompt_part.split("Recommended Compute:")[0].strip()
                    compute_override = prompt_part.split("Recommended Compute:")[-1].strip().lower()
                else:
                    prompt = prompt_part.strip()

                return {"prompt": prompt, "compute_override": compute_override}
            except Exception:
                return {"prompt": f"Continue with previous findings.", "compute_override": None}

        # 1. AI-Researcher
        if any(k in lower for k in ["research", "literature", "paper", "review", "survey"]):
            try:
                result = run_ai_researcher(task=f"Research: {challenge}\nContext: {cumulative_context}")
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[AI-Researcher]\n{output}")
                used_tools.append("AI-Researcher")
                cumulative_context += f"\n\n[AI-Researcher Output]\n{output}"
                redesign = reflect_and_redesign(output, "AutoResearch")
                cumulative_context += "\n\n[Arbos Reflection] " + redesign["prompt"]
            except Exception as e:
                results.append(f"[AI-Researcher Error] {str(e)}")

        # 2. AutoResearch
        if any(k in lower for k in ["research", "literature", "paper", "review", "explore", "synthesize"]):
            try:
                redesign = reflect_and_redesign(output if 'output' in locals() else "", "AutoResearch")
                result = run_autoresearch(task=redesign["prompt"])
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[AutoResearch]\n{output}")
                used_tools.append("AutoResearch")
                cumulative_context += f"\n\n[AutoResearch Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + redesign["prompt"]
            except Exception as e:
                results.append(f"[AutoResearch Error] {str(e)}")

        # 3. GPD
        if any(k in lower for k in ["quantum", "physics", "circuit", "theory", "particle", "gravity", "field"]):
            try:
                redesign = reflect_and_redesign(output if 'output' in locals() else "", "GPD")
                result = run_gpd(task=redesign["prompt"], profile="deep-theory")
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[GPD]\n{output}")
                used_tools.append("GPD")
                cumulative_context += f"\n\n[GPD Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + redesign["prompt"]
            except Exception as e:
                results.append(f"[GPD Error] {str(e)}")

        # 4. ScienceClaw
        if any(k in lower for k in ["analyze", "experiment", "data", "science", "conclude"]):
            try:
                redesign = reflect_and_redesign(output if 'output' in locals() else "", "ScienceClaw")
                result = run_scienceclaw(task=redesign["prompt"])
                output = result.get("output", result.get("error", "No output"))
                results.append(f"[ScienceClaw]\n{output}")
                used_tools.append("ScienceClaw")
            except Exception as e:
                results.append(f"[ScienceClaw Error] {str(e)}")

        # Save to long-term memory
        if results:
            memory.add(
                text="\n\n".join(results),
                metadata={"challenge": challenge, "tools_used": ",".join(used_tools)}
            )

        if not results:
            results.append("No specialized tool matched. Using default Arbos reasoning.")
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
