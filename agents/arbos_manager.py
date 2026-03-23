# agents/arbos_manager.py
# COMPLETE FINAL VERSION - Real Arbos + Smart Routing + SDK Compute + Chutes LLM Picker

import os
from dotenv import load_dotenv

# Load .env at startup
load_dotenv()

import subprocess
import time
from agents.tools.reflection import reflect_and_improve
from agents.tools.gpd import run_gpd
from agents.tools.scienceclaw import run_scienceclaw
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.hyperagent import run_hyperagent
from agents.tools.exploration import explore_novel_variant
from agents.tools.resource_aware import ResourceMonitor
from agents.tools.guardrails import apply_guardrails
from agents.tools.compute import ComputeRouter

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        load_dotenv()
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self._setup_real_arbos()
        print(f"✅ REAL Arbos + Compute + Timing loaded ({self.compute.get_compute()})")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("📥 Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unconst/Arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {"reflection": 3, "hyper_planning": False, "exploration": False, "resource_aware": True, "guardrails": True}
        try:
            with open(self.goal_file, "r") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("reflection:"): config["reflection"] = int(line.split(":")[1])
                    elif line.startswith("hyper_planning:"): config["hyper_planning"] = "true" in line
                    elif line.startswith("exploration:"): config["exploration"] = "true" in line
                    elif line.startswith("resource_aware:"): config["resource_aware"] = "true" in line
                    elif line.startswith("guardrails:"): config["guardrails"] = "true" in line
        except:
            pass
        return config

    def _smart_route(self, challenge: str):
        lower = challenge.lower()
        results = []
        if any(k in lower for k in ["quantum", "physics", "circuit"]): results.append(run_gpd(challenge))
        if any(k in lower for k in ["discover", "biology", "material"]): results.append(run_scienceclaw(challenge, 20))
        if any(k in lower for k in ["research", "paper", "literature"]): results.append(run_ai_researcher(challenge))
        if self.config.get("hyper_planning"): results.append(run_hyperagent(challenge))
        return "\n\n".join(results), ["GPD", "ScienceClaw", "AI-Researcher"]

    def run(self, challenge: str):
        monitor = ResourceMonitor(max_hours=3.8)
        print(f"🔀 Running REAL Arbos with {self.compute.get_compute()} compute...")

        try:
            tool_results, tools_used = self._smart_route(challenge)
            initial_input = f"Challenge: {challenge}\nTools:\n{tool_results}"
            
            result = subprocess.run([
                "python", f"{self.arbos_path}/arbos.py",
                "--goal", self.goal_file,
                "--input", initial_input
            ], capture_output=True, text=True, timeout=3600)
            
            arbos_output = result.stdout.strip()

            # Real LLM reflection using chosen Chutes model
            def real_llm_call(prompt):
                return self.compute.run_on_compute(prompt)

            final_output, trace = reflect_and_improve(
                task=challenge,
                output=arbos_output,
                llm_call=real_llm_call,
                max_iterations=self.config.get("reflection", 3)
            )

            final_output = monitor.check_and_compress(final_output)
            if self.config.get("exploration"):
                final_output = explore_novel_variant(challenge, final_output)
            if self.config.get("guardrails"):
                final_output = apply_guardrails(final_output, monitor.elapsed_hours())

        except Exception as e:
            final_output = f"ERROR: {str(e)}"

        return {
            "solution": final_output,
            "status": "complete",
            "tools_used": tools_used,
            "compute_used": self.compute.get_compute()
        }
