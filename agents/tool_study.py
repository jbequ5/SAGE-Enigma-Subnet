# agents/tool_study.py
# Tool Study Phase - Arbos deeply studies each tool and builds high-fidelity mimic profiles
# All calls go through ComputeRouter (no direct run_hyperagent)

from pathlib import Path

class ToolStudy:
    def __init__(self):
        self.profiles_dir = Path("tool_profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        # Import ComputeRouter here to avoid circular imports
        from agents.tools.compute import ComputeRouter
        self.compute = ComputeRouter()

    def study_all_tools(self):
        """Run this once. Arbos studies each tool and saves detailed profiles."""
        tools = {
            "AI-Researcher": "https://github.com/HKUDS/AI-Researcher",
            "AutoResearch": "https://github.com/karpathy/autoresearch",
            "GPD": "https://github.com/psi-oss/get-physics-done",
            "ScienceClaw": "https://github.com/lamm-mit/scienceclaw",
            "HyperAgent": "https://github.com/facebookresearch/HyperAgents"
        }

        print("🔬 Starting Tool Study Phase... Arbos is learning all tools.\n")

        for tool_name, repo_url in tools.items():
            print(f"Studying {tool_name}...")
            profile = self._study_tool(tool_name, repo_url)
            self._save_profile(tool_name, profile)
            print(f"✅ Profile for {tool_name} saved.\n")

        print("✅ Tool Study Phase completed! All profiles are ready.")

    def _study_tool(self, tool_name: str, repo_url: str) -> str:
        study_task = f"""
You are Arbos, a highly intelligent agent conductor.
Carefully study the tool "{tool_name}" at {repo_url}.

Provide a detailed, technical profile including:
- Core purpose and unique strengths
- Exact workflow and iteration style
- How it uses memory or persistent state
- What makes it different from a generic LLM call
- Best prompting techniques to accurately mimic its behavior
- Ideal use cases and known limitations

Be precise and comprehensive. Focus on what makes this tool valuable for novelty, depth, and intelligence.
"""

        # All study calls go through ComputeRouter
        result = self.compute.run_on_compute(study_task)
        return result

    def _save_profile(self, tool_name: str, profile: str):
        path = self.profiles_dir / f"{tool_name.lower()}.md"
        path.write_text(profile)

    def load_profile(self, tool_name: str) -> str:
        path = self.profiles_dir / f"{tool_name.lower()}.md"
        if path.exists():
            return path.read_text()
        return f"No profile found for {tool_name}. Using high-intelligence generic reasoning."

# Global instance
tool_study = ToolStudy()
