# agents/arbos_manager.py
# Final integrated Arbos Manager for Enigma Machine
# Reads GOAL.md toggles + calls real tools from GitHub

import os
from agents.tools.reflection import reflect_and_improve
from agents.tools.gpd import run_gpd
from agents.tools.scienceclaw import run_scienceclaw
from agents.tools.planning import create_plan
from agents.tools.exploration import explore_novel_variant
from agents.tools.resource_aware import check_and_compress
from agents.tools.guardrails import apply_guardrails

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        self.config = self._load_config()
        print(f"✅ Arbos loaded with GOAL: {goal_file}")

    def _load_config(self):
        """Parse simple key: value from GOAL.md"""
        config = {
            "reflection": 3,
            "planning": True,
            "multi_agent": True,
            "swarm_size": 20,
            "exploration": False,
            "resource_aware": True,
            "guardrails": True
        }
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    if line.strip().startswith("reflection:"):
                        config["reflection"] = int(line.split(":")[1].strip())
                    elif line.strip().startswith("planning:"):
                        config["planning"] = "true" in line.lower()
                    elif line.strip().startswith("multi_agent:"):
                        config["multi_agent"] = "true" in line.lower()
                    elif line.strip().startswith("swarm_size:"):
                        config["swarm_size"] = int(line.split(":")[1].strip())
                    elif line.strip().startswith("exploration:"):
                        config["exploration"] = "true" in line.lower()
                    elif line.strip().startswith("resource_aware:"):
                        config["resource_aware"] = "true" in line.lower()
                    elif line.strip().startswith("guardrails:"):
                        config["guardrails"] = "true" in line.lower()
        except:
            pass
        return config

    def run(self, challenge: str):
        print(f"🔥 Starting Enigma challenge: {challenge[:100]}...")

        # 1. Planning (optional)
        if self.config["planning"]:
            plan = create_plan(challenge)

        # 2. Tool execution
        gpd_result = run_gpd(challenge)
        scienceclaw_result = run_scienceclaw(challenge, self.config["swarm_size"])

        initial_output = f"GPD: {gpd_result}\nScienceClaw: {scienceclaw_result}"

        # 3. Reflection (always recommended)
        final_output, trace = reflect_and_improve(
            task=challenge,
            output=initial_output,
            llm_call=lambda x: f"Improved version: {x}",  # Replace with real LLM later
            max_iterations=self.config.get("reflection", 3)
        )

        # 4. Exploration (optional)
        if self.config["exploration"]:
            final_output = explore_novel_variant(challenge, final_output)

        # 5. Resource check
        if self.config["resource_aware"]:
            final_output = check_and_compress(3.2, final_output)  # placeholder runtime

        # 6. Guardrails
        if self.config["guardrails"]:
            final_output = apply_guardrails(final_output, 3.5)

        print("✅ Challenge complete!")
        return {
            "solution": final_output,
            "status": "complete",
            "reflection_trace": trace
        }
