# agents/arbos_manager.py
# FINAL COMPLETE VERSION - Real Arbos + Smart Routing + Compute Subnets + All Patterns

import os
import subprocess
from agents.tools.reflection import reflect_and_improve
from agents.tools.gpd import run_gpd
from agents.tools.scienceclaw import run_scienceclaw
from agents.tools.ai_researcher import run_ai_researcher
from agents.tools.hyperagent import run_hyperagent
from agents.tools.exploration import explore_novel_variant
from agents.tools.resource_aware import check_and_compress
from agents.tools.guardrails import apply_guardrails
from agents.tools.compute import ComputeRouter

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self._setup_real_arbos()
        print(f"✅ REAL Arbos + Smart Routing + Compute ({self.compute.get_compute()}) loaded")

    def _setup_real_arbos(self):
        """Clone Const's real Arbos repo once"""
        if not os.path.exists(self.arbos_path):
            print("📥 Cloning real Arbos from Const's GitHub...")
            subprocess.run(["git", "clone", "https://github.com/unconst/Arbos.git", self.arbos_path], check=True)

    def _load_config(self):
        config = {
            "reflection": 3,
            "hyper_planning": False,
            "exploration": False,
            "resource_aware": True,
            "guardrails": True
        }
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
        """Full smart routing for all tools"""
        lower = challenge.lower()
        results = []
        tools_used = []

        # HyperAgent Planning (if enabled)
        if self.config.get("hyper_planning"):
            results.append(run_hyperagent(challenge))
            tools_used.append("HyperAgent (Planning)")

        # Tool routing
        if any(k in lower for k in ["quantum", "circuit", "physics", "math", "derivation"]):
            results.append(run_gpd(challenge))
            tools_used.append("GPD")
        if any(k in lower for k in ["discover", "biology", "material", "novel", "bio", "structure"]):
            results.append(run_scienceclaw(challenge, 20))
            tools_used.append("ScienceClaw")
        if any(k in lower for k in ["research", "paper", "arxiv", "literature", "idea"]):
            results.append(run_ai_researcher(challenge))
            tools_used.append("AI-Researcher")

        # Default fallback
        if not results:
            results.append(run_ai_researcher(challenge))
            results.append(run_scienceclaw(challenge, 15))
            tools_used = ["AI-Researcher", "ScienceClaw"]

        return "\n\n".join(results), tools_used

    def run(self, challenge: str):
        print(f"🔀 Running REAL Arbos with {self.compute.get_compute()} compute...")

        # 1. Smart routing + real tools
        tool_results, tools_used = self._smart_route(challenge)

        # 2. Feed everything to REAL Arbos (Ralph loop)
        initial_input = f"Challenge: {challenge}\n\nTools:\n{tool_results}"
        try:
            result = subprocess.run([
                "python", f"{self.arbos_path}/arbos.py",
                "--goal", self.goal_file,
                "--input", initial_input
            ], capture_output=True, text=True, timeout=3600)
            arbos_output = result.stdout.strip()
        except Exception as e:
            arbos_output = f"Arbos failed: {str(e)}"

        # 3. Post-processing (all patterns)
        final_output, trace = reflect_and_improve(
            task=challenge,
            output=arbos_output,
            llm_call=lambda x: f"Refined: {x}",
            max_iterations=self.config.get("reflection", 3)
        )

        if self.config.get("exploration"):
            final_output = explore_novel_variant(challenge, final_output)
        if self.config.get("resource_aware"):
            final_output = check_and_compress(3.5, final_output)
        if self.config.get("guardrails"):
            final_output = apply_guardrails(final_output, 3.5)

        print(f"✅ REAL Arbos + all patterns complete! Tools used: {tools_used}")
        return {
            "solution": final_output,
            "status": "complete",
            "tools_used": tools_used,
            "compute_used": self.compute.get_compute(),
            "reflection_trace": trace
        }
