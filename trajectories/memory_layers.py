# trajectories/memory_layers.py
# Three-Layer Memory Refinement (short-term + compressed long-term + Vector DB)

import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MemoryLayers:
    def __init__(self, short_term_limit: int = 40, similarity_threshold: float = 0.92):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.short_term: List[Dict] = []          # Layer 1: raw recent trajectories
        self.long_term_summaries: List[Dict] = [] # Layer 2: LLM-compressed summaries
        self.vector_db = None                     # Layer 3: your existing TrajectoryVectorDB
        self.short_term_limit = short_term_limit
        self.similarity_threshold = similarity_threshold

    def set_vector_db(self, vector_db):
        self.vector_db = vector_db

    def add_short_term(self, entry: Dict):
        self.short_term.append(entry)
        if len(self.short_term) > self.short_term_limit:
            self.short_term.pop(0)  # FIFO

    def compress_to_long_term(self, recent_entries: List[Dict], arbos) -> Dict:
        """Use Arbos to compress recent short-term into one concise, deduplicated summary."""
        if not recent_entries:
            return {}
        prompt = f"""Compress these recent trajectories into ONE concise, deduplicated summary (max 300 words). 
        Focus on patterns that improved validation_score. Output JSON: {{"summary": "...", "key_patterns": [...]}}"""
        compressed = arbos.generate(prompt)  # Your existing generate call
        try:
            summary = json.loads(compressed)
        except:
            summary = {"summary": str(compressed)[:300], "key_patterns": []}

        # Deduplicate against existing long-term
        if self.long_term_summaries:
            emb_new = self.model.encode(summary["summary"])
            for old in self.long_term_summaries:
                emb_old = self.model.encode(old["summary"])
                similarity = np.dot(emb_new, emb_old) / (np.linalg.norm(emb_new) * np.linalg.norm(emb_old))
                if similarity > self.similarity_threshold:
                    return {}  # Duplicate, skip
        self.long_term_summaries.append(summary)
        return summary

    def get_context_for_planning(self, query_goal: str, k: int = 8) -> Dict:
        """Layered retrieval for Arbos Recommended / planning."""
        short = self.short_term[-10:] if self.short_term else []
        long_summaries = self.long_term_summaries[-5:] if self.long_term_summaries else []
        vector_results = self.vector_db.search(query_goal, k) if self.vector_db else []
        return {
            "short_term": short,
            "long_term_compressed": long_summaries,
            "vector_retrieved": vector_results
        }
