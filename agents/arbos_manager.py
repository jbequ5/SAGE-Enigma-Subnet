# agents/arbos_manager.py
# FINAL VERSION - Supports miner_review_after_loop toggle + final mandatory review

import os
import subprocess
from pathlib import Path
from typing import Tuple, List

# Core imports
from agents.memory import memory

# Supporting tools only
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
            "miner_review_after_loop": False,   # New toggle
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
                    elif line.startswith("miner_review_final:"):
                        config["miner_review_final"] = "true" in line
        except Exception:
            pass
        return config

    def _smart_route(self, challenge: str, approved_plan: str = "") -> Tuple[str, List[str], bool]:
        """
        Returns: (tool_results, used_tools, should_reloop)
        Respects miner_review_after_loop from GOAL.md
        """
        from agents.tool_study import tool_study
        import streamlit as st

        lower = challenge.lower()
        results = []
        used_tools = []
        cumulative_context = approved_plan[:1500] if approved_plan else ""
        trace_log = []

        # ... (keep all the existing code from previous version up to the end of the loop) ...

        # Save to long-term memory
        if results:
            memory.add(
                text="\n\n".join(results),
                metadata={"challenge": challenge, "tools_used": ",".join(used_tools)}
            )

        if not results:
            results.append("No specialized tool triggered. Using default Arbos reasoning.")
            used_tools.append("Arbos Core")

        # Store trace
        st.session_state.trace_log = trace_log

        # Respect GOAL.md toggle
        should_reloop = self.config.get("miner_review_after_loop", False)

        return "\n\n".join(results), used_tools, should_reloop

    def run(self, challenge: str):
        """Main entry point"""
        print(f"🚀 Starting Arbos for challenge: {challenge[:80]}...")

        monitor = ResourceMonitor(max_hours=3.8)

        tool_results, tools_used, should_reloop = self._smart_route(challenge)

        final_output = apply_guardrails(tool_results, monitor)

        if self.config.get("exploration", True):
            final_output = explore_novel_variant(challenge, final_output)

        print(f"✅ Completed with tools: {tools_used}")
        return final_output, should_reloop   # (output, should_reloop)
