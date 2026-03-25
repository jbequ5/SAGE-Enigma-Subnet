# agents/arbos_manager.py
# FINAL OPERATIONAL VERSION - Reflection after every tool + Long-term memory + program.md

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

from agents.memory import memory
from agents.tools.hyperagent import run_hyperagent
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.autoresearch import run_autoresearch
from agents.tools.get_physics_done import run_gpd
from agents.tools.scienceclaw import run_scienceclaw
from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails
from agents.tools.exploration import explore_novel_variant   # optional

class ArbosManager:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self._setup_real_arbos()
        print("✅ REAL Arbos + Long-term Memory + Reflection Loop loaded")

    def _setup_real_arbos(self):
        """Clone real Arbos if not present"""
        if not os.path.exists(self.arbos_path):
            print("Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        """Load settings from GOAL.md"""
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
        """Full sequential routing with reflection + prompt redesign AFTER EVERY TOOL"""
        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = approved_plan[:1500] if approved_plan else ""

        # Long-term memory retrieval
        past_knowledge = memory.query(challenge, n_results=4)
        if past_knowledge:
            cumulative_context += "\n\nRelevant past knowledge from previous runs:\n" + "\n---\n".join(past_knowledge)

        # Initialize program.md for AutoResearch
        program_path = Path("program.md")
        if not program_path.exists():
            program_path.write_text(f"# Execution Program\n\n## Challenge\n{challenge}\n\n## Approved Plan\n{approved_plan}\n\n")

        # Helper: Arbos reflection + prompt redesign
        def reflect_and_redesign(last_output: str, next_tool: str) -> str:
            try:
                task = f"""Previous tool output: {last_output}
Overall goal: {challenge}
Next tool: {next_tool}

Reconstruct the previous output into a specific, high-quality prompt for the next tool.
Maintain the overall goal and evaluation criteria throughout.
Write the exact prompt that should be sent to the next tool."""
                result = run_hyperagent(task=task, parallel_tasks=3)
                return result.get("output", f"Continue with previous findings: {last_output[:600]}")
            except Exception:
                return f"Continue with previous findings: {last_output[:600]}"

        # 1. AI-Researcher
        if any(k in lower for k in ["research", "literature", "paper", "review", "survey"]):
            try:
                cfg = self.config.get("AI-Researcher", {})
                mode = cfg.get("search_mode", "deep")

                task = f"Challenge: {challenge}\nPlan context: {cumulative_context}\nPerform broad search."

                result = run_ai_researcher(task=task, search_mode=mode)
                output = result.get("output", result.get("error", ""))
                results.append(f"[AI-Researcher — {mode}]\n{output}")
                used_tools.append("AI-Researcher")
                cumulative_context += f"\n\n[AI-Researcher Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + reflect_and_redesign(output, "AutoResearch")
            except Exception as e:
                results.append(f"[AI-Researcher Error] {str(e)}")

        # 2. AutoResearch
        if any(k in lower for k in ["research", "literature", "paper", "review", "explore", "synthesize"]):
            try:
                cfg = self.config.get("AutoResearch", {})
                depth = cfg.get("depth", "medium")
                iterations = cfg.get("iterations", 3)

                task = cumulative_context

                result = run_autoresearch(task=task, depth=depth, iterations=iterations, program_md_path=str(program_path))
                output = result.get("output", result.get("error", ""))
                results.append(f"[AutoResearch — depth:{depth}, iterations:{iterations}]\n{output}")
                used_tools.append("AutoResearch")
                cumulative_context += f"\n\n[AutoResearch Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + reflect_and_redesign(output, "GPD")
            except Exception as e:
                results.append(f"[AutoResearch Error] {str(e)}")

        # 3. GPD
        if any(k in lower for k in ["quantum", "physics", "circuit", "theory", "particle", "gravity", "field"]):
            try:
                cfg = self.config.get("GPD", {})
                profile = cfg.get("profile", "deep-theory")
                tier = cfg.get("tier", "1")

                task = cumulative_context

                result = run_gpd(task=task, profile=profile, tier=tier)
                output = result.get("output", result.get("error", ""))
                results.append(f"[GPD — {profile} / Tier {tier}]\n{output}")
                used_tools.append("GPD")
                cumulative_context += f"\n\n[GPD Output]\n{output}"
                cumulative_context += "\n\n[Arbos Reflection] " + reflect_and_redesign(output, "ScienceClaw")
            except Exception as e:
                results.append(f"[GPD Error] {str(e)}")

        # 4. ScienceClaw
        if any(k in lower for k in ["analyze", "experiment", "data", "science", "conclude"]):
            try:
                cfg = self.config.get("ScienceClaw", {})
                intensity = cfg.get("search_intensity", "high")
                max_src = cfg.get("max_sources", 15)

                task = cumulative_context

                result = run_scienceclaw(task=task, search_intensity=intensity, max_sources=max_src)
                output = result.get("output", result.get("error", ""))
                results.append(f"[ScienceClaw — {intensity}]\n{output}")
                used_tools.append("ScienceClaw")
            except Exception as e:
                results.append(f"[ScienceClaw Error] {str(e)}")

        # Save final results to long-term memory
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
        """Main entry point for the miner"""
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        # Run the full smart route
        tool_results, tools_used = self._smart_route(challenge)

        # Final guardrails and optional exploration
        final_output = apply_guardrails(tool_results)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(final_output, challenge)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output
