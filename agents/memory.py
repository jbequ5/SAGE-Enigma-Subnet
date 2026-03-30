from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import datetime
import json
from typing import List, Dict, Any

class LongTermMemory:
    """Your original ChromaDB backend - 100% preserved."""
    def __init__(self, db_path="memory_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(name="enigma_memory")

    def add(self, text: str, metadata: dict = None):
        if metadata is None:
            metadata = {}
        metadata["timestamp"] = str(datetime.datetime.now())
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(hash(text + str(datetime.datetime.now())))]
        )

    def query(self, query_text: str, n_results: int = 5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results.get('documents', [[]])[0]


class MemoryLayers:
    """Three-layer memory system with light compression (integrated into memory.py)."""
    def __init__(self):
        self.long_term = LongTermMemory()           # Layer 3: Persistent vector DB
        self.short_term: List[Dict] = []            # Layer 1: Recent raw trajectories
        self.long_term_summaries: List[Dict] = []   # Layer 2: Compressed summaries
        self.tool_proposals: List[str] = []         # Tool suggestions only (no creation)

    def add(self, text: str, metadata: dict = None):
        """Add to short-term layer."""
        if metadata is None:
            metadata = {}
        entry = {"text": text, "metadata": metadata, "timestamp": datetime.datetime.now().isoformat()}
        self.short_term.append(entry)
        
        # Keep short-term reasonable size
        if len(self.short_term) > 40:
            self.compress_to_long_term()

        # Also store in long-term vector DB
        self.long_term.add(text, metadata)

    def add_proposals(self, proposals: List[str]):
        """Lightweight tool proposals (suggestions only)."""
        self.tool_proposals.extend(proposals)
        for p in proposals:
            self.add(f"TOOL PROPOSAL: {p}", {"type": "tool_proposal"})

    def compress_to_long_term(self):
        """Compress oldest short-term entries into summaries."""
        if not self.short_term:
            return
        to_compress = self.short_term[:10]
        self.short_term = self.short_term[10:]

        summary_text = "\n".join([entry["text"][:500] for entry in to_compress])
        summary_entry = {
            "summary": summary_text[:2000],
            "original_count": len(to_compress),
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "compressed_summary"
        }
        self.long_term_summaries.append(summary_entry)
        self.long_term.add(summary_text, {"type": "compressed_summary"})

    def compress_low_value(self, current_score: float = 0.0):
        """Light threshold-triggered compression - called from re_adapt."""
        # Remove very low-value entries
        self.short_term = [entry for entry in self.short_term if entry.get("metadata", {}).get("local_score", 0.5) > 0.4]
        
        if len(self.short_term) > 25:
            self.compress_to_long_term()

    def get_total_context_tokens(self) -> int:
        """Rough token estimate for compression triggering."""
        total = 0
        for entry in self.short_term:
            total += len(entry["text"]) // 4
        for entry in self.long_term_summaries:
            total += len(entry["summary"]) // 4
        return total

    def query(self, query_text: str, n_results: int = 5):
        """Query long-term vector DB."""
        return self.long_term.query(query_text, n_results)

    def get_recent_context(self, max_items: int = 8) -> str:
        """Get recent + compressed context for prompts."""
        recent = self.short_term[-max_items:]
        summaries = self.long_term_summaries[-3:]
        
        context = "RECENT TRAJECTORIES:\n"
        for item in recent:
            context += f"- {item['text'][:300]}...\n"
        
        if summaries:
            context += "\nCOMPRESSED PATTERNS:\n"
            for s in summaries:
                context += f"- {s['summary'][:400]}...\n"
        
        return context


# Global instances
memory = LongTermMemory()
memory_layers = MemoryLayers()   # This is what ArbosManager will use
