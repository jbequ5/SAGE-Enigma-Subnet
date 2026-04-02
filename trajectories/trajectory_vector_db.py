import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from datetime import datetime, timedelta
import logging
import torch
import psutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrajectoryVectorDB:
    def __init__(self, base_max_entries: int = 2000):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dim = 384

        # Hardware-aware initialization
        self.ram_gb = psutil.virtual_memory().total / (1024**3)
        self.vram_gb = self._get_vram_gb()
        self.cpu_cores = psutil.cpu_count(logical=False)

        self.max_entries = self._compute_adaptive_max_entries(base_max_entries)
        self.index = self._create_adaptive_index()

        self.trajectories = []          # Full raw data
        self.compressed_deltas = []     # Compressed versions from Intelligence Layer

        self.path = Path("trajectories")
        self.meta_path = self.path / "vector_meta.jsonl"
        self.path.mkdir(exist_ok=True)

        self.load()
        logger.info(f"✅ TrajectoryVectorDB initialized | Max: {self.max_entries} | VRAM: {self.vram_gb:.1f}GB | RAM: {self.ram_gb:.1f}GB")

    def _get_vram_gb(self) -> float:
        try:
            if torch.cuda.is_available():
                return torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return 0.0
        except:
            return 0.0

    def _compute_adaptive_max_entries(self, base: int) -> int:
        """Smart scaling based on real hardware."""
        ram_factor = min(1.0, self.ram_gb / 16)
        vram_factor = min(1.0, self.vram_gb / 8) if self.vram_gb > 4 else 0.4
        core_factor = min(1.0, self.cpu_cores / 8)

        adaptive = int(base * ram_factor * vram_factor * core_factor * 0.85)
        return max(600, min(adaptive, 3500))  # Safe, intelligent bounds

    def _create_adaptive_index(self):
        """Choose best index type based on hardware."""
        if self.vram_gb >= 6.0:
            index = faiss.IndexHNSWFlat(self.dim, 32)
            index.hnsw.efConstruction = 300
            index.hnsw.efSearch = 80
            logger.info("Using HNSW (high-performance)")
        else:
            index = faiss.IndexFlatL2(self.dim)
            logger.info("Using FlatL2 (memory efficient)")
        return index

    def _get_embedding_text(self, traj: dict) -> str:
        score = traj.get("validation_score", traj.get("local_score", 0.0))
        fidelity = traj.get("fidelity", 0.5)
        hetero = traj.get("heterogeneity_score", 0.0)
        
        return (
            f"Score:{score:.3f} Fidelity:{fidelity:.3f} Hetero:{hetero:.3f} "
            f"Challenge:{traj.get('challenge', '')[:300]} "
            f"Solution:{str(traj.get('solution', ''))[:1100]}"
        )

    def embed(self, traj: dict) -> np.ndarray:
        text = self._get_embedding_text(traj)
        emb = self.model.encode(text, normalize_embeddings=True)
        return emb.astype('float32')

    def _compute_value(self, traj: dict) -> float:
        """Reinforcement-aware value for pruning."""
        score = traj.get("validation_score", 0.0)
        fidelity = traj.get("fidelity", 0.5)
        hetero = traj.get("heterogeneity_score", 0.5)
        age_days = (datetime.now() - datetime.fromisoformat(traj.get("timestamp", "2024-01-01"))) / timedelta(days=1)
        
        return (score ** 1.7) * (fidelity ** 1.9) * (hetero ** 1.3) * np.exp(-age_days * 0.1)

    def add(self, traj: dict, compress: bool = True):
        """Add trajectory with optional compression integration."""
        if not traj:
            return

        # Integrate with Compression Layer
        if compress and hasattr(self, 'arbos') and self.arbos is not None:
            try:
                raw_context = json.dumps(traj)
                compressed = self.arbos.compress_intelligence_delta(raw_context)
                traj["compressed_delta"] = compressed[:2000]  # Store summary
            except:
                pass

        emb = self.embed(traj)
        self.index.add(np.array([emb]))
        self.trajectories.append(traj)

        if len(self.trajectories) > self.max_entries:
            self.trajectories.sort(key=self._compute_value, reverse=True)
            self.trajectories = self.trajectories[:self.max_entries]
            self._rebuild_index()

        # Persistent storage
        try:
            with open(self.meta_path, "a", encoding="utf-8") as f:
                copy = traj.copy()
                copy["timestamp"] = datetime.now().isoformat()
                copy["value"] = self._compute_value(traj)
                f.write(json.dumps(copy) + "\n")
        except Exception as e:
            logger.warning(f"Persist failed: {e}")

    def add_eggroll(self, traj: dict, perturbation_info: dict = None):
        if perturbation_info:
            traj["eggroll_perturbation"] = perturbation_info
            traj["heterogeneity_score"] = traj.get("heterogeneity_score", 0) + 0.18
        self.add(traj)

    def search(self, query_goal: str, k: int = 12, min_score: float = 0.0, min_fidelity: float = 0.0):
        if not self.trajectories:
            return []

        q_emb = self.model.encode(query_goal, normalize_embeddings=True).astype('float32')
        D, I = self.index.search(np.array([q_emb]), min(k * 4, len(self.trajectories)))

        results = []
        for idx in I[0]:
            if idx >= len(self.trajectories):
                continue
            traj = self.trajectories[idx]
            if traj.get("validation_score", 0) >= min_score and traj.get("fidelity", 0) >= min_fidelity:
                results.append(traj)
            if len(results) >= k:
                break

        # Final re-ranking
        if results:
            results.sort(
                key=lambda x: self._compute_value(x),
                reverse=True
            )
        return results[:k]

    def _rebuild_index(self):
        self.index.reset()
        if self.trajectories:
            embeddings = np.array([self.embed(t) for t in self.trajectories])
            self.index.add(embeddings)

    def load(self):
        if self.meta_path.exists():
            try:
                with open(self.meta_path, encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            traj = json.loads(line)
                            self.trajectories.append(traj)
                            self.index.add(np.array([self.embed(traj)]))
            except Exception as e:
                logger.error(f"Load error: {e}")

        logger.info(f"Loaded {len(self.trajectories)} trajectories | Adaptive max: {self.max_entries}")

    def get_stats(self):
        return {
            "total": len(self.trajectories),
            "max_entries": self.max_entries,
            "ram_gb": round(self.ram_gb, 1),
            "vram_gb": round(self.vram_gb, 1),
            "index_type": "HNSW" if hasattr(self.index, 'hnsw') else "FlatL2"
        }

    def clear(self):
        self.index.reset()
        self.trajectories.clear()
        if self.meta_path.exists():
            self.meta_path.unlink()
        logger.info("TrajectoryVectorDB cleared.")

# Global instance
vector_db = TrajectoryVectorDB()
