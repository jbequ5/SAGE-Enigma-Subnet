# agents/tool_study.py
# Upgraded Tool Study - Vector retrieval + Self-refinement on profiles

from pathlib import Path
from agents.tools.compute import ComputeRouter
import chromadb
from chromadb.utils import embedding_functions

class ToolStudy:
    def __init__(self):
        self.profiles_dir = Path("tool_profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        self.compute = ComputeRouter()

        # Vector store for profile chunks
        self.client = chromadb.PersistentClient(path="tool_profiles_vector")
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(name="tool_profiles")

    def study_all_tools(self):
        """Run once. Study + self-refine each tool."""
        tools = {
            "AI-Researcher": "https://github.com/HKUDS/AI-Researcher",
            "AutoResearch": "https://github.com/karpathy/autoresearch",
            "GPD": "https://github.com/psi-oss/get-physics-done",
            "ScienceClaw": "https://github.com/lamm-mit/scienceclaw",
            "HyperAgent": "https://github.com/facebookresearch/HyperAgents"
        }

        print("🔬 Starting Upgraded Tool Study Phase (with self-refinement)...\n")

        for tool_name, repo_url in tools.items():
            print(f"Studying {tool_name}...")

            # Pass 1: Initial study
            initial_profile = self._study_tool(tool_name, repo_url)

            # Pass 2: Self-refinement
            refined_profile = self._self_refine_profile(tool_name, initial_profile)

            # Save to vector store (chunked)
            self._save_to_vector(tool_name, refined_profile)

            print(f"✅ Refined profile for {tool_name} saved to vector store.\n")

        print("✅ Upgraded Tool Study completed.")

    def _study_tool(self, tool_name: str, repo_url: str) -> str:
        study_task = f"""
Study the tool "{tool_name}" at {repo_url}.
Provide a detailed profile covering purpose, workflow, strengths, limitations, and how to mimic it.
"""
        return self.compute.run_on_compute(study_task)

    def _self_refine_profile(self, tool_name: str, initial_profile: str) -> str:
        refine_task = f"""
You are Arbos performing self-refinement.

Initial Profile for {tool_name}:
{initial_profile}

Critique this profile for:
- Completeness
- Accuracy
- Usefulness for mimicking in a tight reflection loop
- Potential to improve solution novelty and verifier score

Then produce an improved, refined profile.
Add a short section: "Improvement Potential for Enigma Miner"
"""
        return self.compute.run_on_compute(refine_task)

    def _save_to_vector(self, tool_name: str, profile: str):
        """Save profile as chunked documents for vector retrieval"""
        # Split into reasonable chunks
        chunks = [profile[i:i+800] for i in range(0, len(profile), 800)]
        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                metadatas=[{"tool": tool_name, "chunk_id": i}],
                ids=[f"{tool_name}_{i}"]
            )

    def load_relevant_profile(self, tool_name: str, query: str, n_results: int = 3) -> str:
        """Retrieve the most relevant chunks for the current context"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"tool": tool_name}
        )
        if results and results["documents"]:
            return "\n\n".join(results["documents"][0])
        return f"No profile found for {tool_name}. Using high-intelligence generic reasoning."

# Global instance
tool_study = ToolStudy()
