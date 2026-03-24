# agents/arbos_manager.py
# FINAL COMPLETE VERSION - Real Arbos + Smart Routing + SDK Compute + Chutes LLM Picker

import os
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
from agents.tools.get_physics_done import run_gpd    

class ArbosManager:
    def __init__(self, goal_file="goals/killer_base.md"):
        self.goal_file = goal_file
        self.arbos_path = "agents/arbos"
        self.compute = ComputeRouter()
        self.config = self._load_config()
        self._setup_real_arbos()
        print(f"✅ REAL Arbos + Compute + Chutes LLM ({self.compute.config.get('chutes_llm', 'mixtral')}) loaded")

    def _setup_real_arbos(self):
        if not os.path.exists(self.arbos_path):
            print("📥 Cloning real Arbos...")
            subprocess.run(["git", "clone", "https://github.com/unarbos/arbos.git", self.arbos_path], check=True)

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
    """
    Smart routing with real Get Physics Done integration.
    Uses the user's personal config from GOAL.md / UI.
    """
    lower = challenge.lower()
    results = []
    used_tools = []

    # === GPD (Get Physics Done) Routing ===
    if any(k in lower for k in ["quantum", "physics", "circuit", "theory", "particle", "gravity", "field"]):
        try:
            from agents.tools.get_physics_done import run as run_gpd
            
            # Get user's personal GPD config (from GOAL.md or session)
            gpd_config = self.config.get("GPD", {}) if isinstance(self.config, dict) else {}
            profile = gpd_config.get("profile", "deep-theory")
            tier = gpd_config.get("tier", "1")

            gpd_result = run_gpd(
                task=challenge,
                profile=profile,
                tier=tier
            )

            if gpd_result.get("success"):
                results.append(f"[GPD - {profile} / Tier {tier}]\n{gpd_result['output']}")
            else:
                results.append(f"[GPD Error] {gpd_result.get('error', 'Unknown error')}")
            
            used_tools.append("GPD")
            
        except Exception as e:
            results.append(f"[GPD Exception] {str(e)}")
            used_tools.append("GPD (failed)")

    # === Other tools (keep your existing logic) ===
    if any(k in lower for k in ["discover", "biology", "material", "chemistry"]):
        results.append(run_scienceclaw(challenge, 20))
        used_tools.append("ScienceClaw")

    if any(k in lower for k in ["research", "paper", "literature", "review"]):
        results.append(run_ai_researcher(challenge))
        used_tools.append("AI-Researcher")

    if self.config.get("hyper_planning", False):
        results.append(run_hyperagent(challenge))
        used_tools.append("HyperAgent")

    # Fallback if nothing matched
    if not results:
        results.append("No specialized tool matched. Using default Arbos reasoning.")
        used_tools.append("Arbos Core")

    return "\n\n".join(results), used_tools
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

            # Real LLM reflection using chosen Chutes model (mixtral, llama3, gemma2, etc.)
            def real_llm_call(prompt):
                return self.compute.run_on_compute(prompt)

            final_output, trace = reflect_and_improve(
                task=challenge,
                output=arbos_output,
                llm_call=real_llm_call,
                max_iterations=self.config.get("reflection", 3)
            )

            # Post-processing
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
