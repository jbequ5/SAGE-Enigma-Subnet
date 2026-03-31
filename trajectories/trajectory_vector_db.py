import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrajectoryVectorDB:
    def __init__(self, dim: int = 384, max_entries: int = 500):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(dim)
        self.trajectories = []
        self.path = Path("trajectories")
        self.meta_path = self.path / "vector_meta.jsonl"
        self.max_entries = max_entries
        self.path.mkdir(exist_ok=True)
        self.load()

    def embed(self, traj: dict) -> np.ndarray:
        # Clean text for embedding (remove noisy fields)
        clean_traj = {k: v for k, v in traj.items() 
                     if k not in ["embedding", "timestamp", "eggroll_perturbation", "reached_content"]}
        text = json.dumps(clean_traj)
        return self.model.encode(text).astype('float32')

    def add(self, traj: dict):
        emb = self.embed(traj)
        self.index.add(np.array([emb]))
        self.trajectories.append(traj)
        
        # Prune to max_entries keeping highest-scoring ones
        if len(self.trajectories) > self.max_entries:
            self.trajectories.sort(key=lambda x: x.get("validation_score", 0), reverse=True)
            self.trajectories = self.trajectories[:self.max_entries]
            # Rebuild index with top entries
            self.index.reset()
            for t in self.trajectories:
                self.index.add(np.array([self.embed(t)]))

        # Append to persistent log
        with open(self.meta_path, "a") as f:
            traj_copy = traj.copy()
            traj_copy["timestamp"] = datetime.now().isoformat()
            f.write(json.dumps(traj_copy) + "\n")

    def add_eggroll(self, traj: dict, perturbation_info: dict = None):
        """Add trajectory with EGGROLL perturbation info."""
        if perturbation_info:
            traj["eggroll_perturbation"] = perturbation_info
        self.add(traj)

    def search(self, query_goal: str, k: int = 8):
        """Semantic search for relevant past trajectories."""
        if not self.trajectories:
            return []
        q_emb = self.model.encode(query_goal).astype('float32')
        D, I = self.index.search(np.array([q_emb]), k)
        return [self.trajectories[i] for i in I[0] if i < len(self.trajectories)]

    def load(self):
        """Load persisted trajectories on startup."""
        if self.meta_path.exists():
            with open(self.meta_path) as f:
                for line in f:
                    if line.strip():
                        try:
                            traj = json.loads(line)
                            self.trajectories.append(traj)
                            emb = self.embed(traj)
                            self.index.add(np.array([emb]))
                        except Exception as e:
                            logger.warning(f"Failed to load trajectory line: {e}")
            logger.info(f"Loaded {len(self.trajectories)} trajectories from vector DB")

    def clear(self):
        """Clear index and trajectories (useful for testing)."""
        self.index.reset()
        self.trajectories = []
        if self.meta_path.exists():
            self.meta_path.unlink()
        logger.info("TrajectoryVectorDB cleared.")

# Global instance
vector_db = TrajectoryVectorDB()
