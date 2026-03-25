# agents/tool_study.py
# Tool Study Phase - Arbos learns the real tools and builds mimic profiles

import os
from pathlib import Path
from agents.tools.hyperagent import run_hyperagent

class ToolStudy:
    def __init__(self):
        self.profiles_dir = Path("tool_profiles")
        self.profiles_dir.mkdir(exist_ok=True)

    def study_all_tools(self):
        """Study all tools and save profiles"""
        tools = {
            "AutoResearch": "https://github.com/karpathy/autoresearch",
            "GPD": "https://github.com/psi-oss/get-physics-done",
            "ScienceClaw": "https://github.com/lamm-mit/scienceclaw",
            "AI-Researcher": "https://github.com/HKUDS/AI-Researcher"
        }

        for tool_name, repo_url in tools.items():
            print(f"Studying {tool_name}...")
            profile = self._study_tool(tool_name, repo_url)
            self._save_profile(tool_name, profile)
            print(f"✅ Profile for {tool_name} saved")

    def _study_tool(self, tool_name: str, repo_url: str):
        study_task = f"""
You are Arbos, a highly intelligent agent conductor.
Study the tool "{tool_name}" at {repo_url}.

Extract and summarize:
- Core purpose and unique strengths
- How it actually works (workflow, iteration style, memory usage)
- What makes it special compared to a generic LLM call
- Key behaviors, limitations, and ideal use cases
- How to best mimic its behavior using a strong LLM prompt

Be detailed and precise. Focus on what makes this tool valuable for novelty and intelligence.
"""

        result = run_hyperagent(task=study_task, parallel_tasks=3)
        return result.get("output", "Study failed")

    def _save_profile(self, tool_name: str, profile: str):
        path = self.profiles_dir / f"{tool_name.lower()}.md"
        path.write_text(profile)

    def load_profile(self, tool_name: str) -> str:
        path = self.profiles_dir / f"{tool_name.lower()}.md"
        if path.exists():
            return path.read_text()
        return f"No profile found for {tool_name}. Using generic reasoning."

# Global instance
tool_study = ToolStudy()
