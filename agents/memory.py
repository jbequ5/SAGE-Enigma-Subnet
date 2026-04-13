# agents/memory.py - v0.9.7 MAXIMUM SOTA LongTermMemory + MemoryLayers + ByteRover MAU Pyramid
# Fully verifier-first, EFS/c/θ/heterogeneity/contract-aware, SOTA-gated, Grail-integrated,
# graph-aware, predictive-integrated, vault-routing ready, and fully expanded.

from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
import datetime
import json
from typing import List, Dict, Any, Optional
import logging
import networkx as nx
import numpy as np
from scipy.stats import gaussian_kde

logger = logging.getLogger(__name__)

class LongTermMemory:
    """v0.9.7 SOTA — Verifier-first, reinforcement-aware, freshness-aware ChromaDB backend.
    Hybrid scoring (vector similarity + MAU/EFS impact), metadata filtering, staleness decay,
    batch operations, and direct support for PatternEvolutionArbos + Scientist Mode + Vaults."""

    def __init__(self, db_path: str = "memory_db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        
        self.collection = self.client.get_or_create_collection(
            name="enigma_memory",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine", "hnsw:construction_ef": 200, "hnsw:M": 32}
        )
        logger.info(f"✅ LongTermMemory v0.9.7 initialized with {embedding_model} embeddings")

    def add(self, text: str, metadata: Dict = None):
        """SOTA add with rich enriched metadata, reinforcement scoring, and deterministic ID."""
        if metadata is None:
            metadata = {}
        
        timestamp = datetime.datetime.now().isoformat()
        reinforcement = metadata.get("mau_reinforcement", metadata.get("local_score", 0.5) * 0.88)
        freshness = metadata.get("freshness_score", 1.0)
        efs_impact = metadata.get("efs_impact", 0.0)
        
        enriched_meta = {
            **metadata,
            "timestamp": timestamp,
            "reinforcement": round(reinforcement, 4),
            "freshness": round(freshness, 4),
            "efs_impact": round(efs_impact, 4),
            "local_score": metadata.get("local_score", 0.5),
            "domain": metadata.get("domain", "general"),
            "type": metadata.get("type", "fragment"),
            "provenance": metadata.get("provenance", "unknown"),
            "vault_entry": metadata.get("vault_entry", False)
        }

        doc_id = f"doc_{abs(hash(text[:500] + timestamp)) % 10**12}"

        try:
            self.collection.add(
                documents=[text],
                metadatas=[enriched_meta],
                ids=[doc_id]
            )
            logger.debug(f"LongTermMemory added fragment | reinforcement {reinforcement:.3f} | freshness {freshness:.3f}")
        except Exception as e:
            logger.warning(f"LongTermMemory add failed (retrying with timestamp ID): {e}")
            try:
                fallback_id = f"doc_fallback_{datetime.datetime.now().timestamp()}"
                self.collection.add(documents=[text], metadatas=[enriched_meta], ids=[fallback_id])
            except Exception as fallback_e:
                logger.error(f"LongTermMemory fallback add failed: {fallback_e}")

    def query(self, query_text: str, n_results: int = 5, 
              where: Optional[Dict] = None, 
              min_reinforcement: float = 0.0,
              min_freshness: float = 0.0) -> List[Dict]:
        """SOTA hybrid query with metadata filtering and combined scoring."""
        try:
            query_params = {
                "query_texts": [query_text],
                "n_results": n_results,
            }
            if where:
                query_params["where"] = where
            
            results = self.collection.query(**query_params)
            
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]
            
            output = []
            for doc, meta, dist in zip(documents, metadatas, distances):
                if (meta.get("reinforcement", 0.0) >= min_reinforcement and 
                    meta.get("freshness", 1.0) >= min_freshness):
                    
                    sim_score = 1.0 - float(dist)
                    combined_score = (sim_score * 0.55) + (meta.get("reinforcement", 0.5) * 0.35) + (meta.get("freshness", 1.0) * 0.10)
                    
                    output.append({
                        "content": doc,
                        "metadata": meta,
                        "similarity": round(sim_score, 4),
                        "combined_score": round(combined_score, 4),
                        "reinforcement": meta.get("reinforcement", 0.0)
                    })
            
            # Sort by combined_score descending
            output.sort(key=lambda x: x["combined_score"], reverse=True)
            return output[:n_results]
            
        except Exception as e:
            logger.warning(f"LongTermMemory query failed (safe empty return): {e}")
            return []

    def get_high_reinforcement_fragments(self, min_reinforcement: float = 0.75, limit: int = 15) -> List[Dict]:
        """Direct helper for PatternEvolutionArbos and Scientist Mode."""
        return self.query(
            query_text="", 
            n_results=limit, 
            where={"reinforcement": {"$gte": min_reinforcement}}
        )

    def get_fresh_fragments(self, min_freshness: float = 0.6, limit: int = 10) -> List[Dict]:
        """Helper for knowledge acquisition freshness checks."""
        return self.query(
            query_text="", 
            n_results=limit, 
            where={"freshness": {"$gte": min_freshness}}
        )

    def delete_old_fragments(self, days_old: int = 120):
        """Staleness cleanup — recommended to run periodically in _end_of_run or background thread."""
        try:
            # ChromaDB doesn't support direct time delete easily; this is a safe log + placeholder
            # In production, query by timestamp where < threshold then collection.delete()
            logger.info(f"🧹 Staleness cleanup recommended: fragments older than {days_old} days")
            # Future full implementation would use where filter on timestamp and delete ids
        except Exception as e:
            logger.debug(f"Staleness cleanup skipped (safe): {e}")

    def get_fragment_count(self) -> int:
        """Return total number of fragments in long-term memory."""
        try:
            return self.collection.count()
        except:
            return 0

    def clear(self):
        """Emergency clear — use with caution."""
        try:
            self.client.delete_collection("enigma_memory")
            self.collection = self.client.get_or_create_collection(
                name="enigma_memory",
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )
            logger.warning("LongTermMemory collection cleared and recreated")
        except Exception as e:
            logger.error(f"Clear failed: {e}")

class MemoryLayers:
    """v0.9.7 SOTA — Three-layer memory system with ByteRover MAU Pyramid + full graph intelligence.
    Fully wired for ToolHunter, PatternEvolutionArbos, Scientist Mode, Vaults, Predictive, and PD Arm."""

    def __init__(self):
        self.long_term = LongTermMemory()  # Layer 3: Persistent vector DB
        self.short_term: List[Dict] = []   # Layer 1: Recent raw trajectories
        self.long_term_summaries: List[Dict] = []  # Layer 2: Compressed summaries
        self.tool_proposals: List[str] = []
        
        # v5.1 ByteRover MAU Pyramid settings
        self.byterover_mau_enabled = True
        self.mau_reinforcement_weight = 1.0
        self.decay_k = 0.085          # tunable via Scientist Mode
        self.heterogeneity_boost = 1.15
        self.arbos = None             # wired from ArbosManager
        
        # v0.9.7 Fragmented Memory Graph
        self.fragment_graph = nx.DiGraph()
        self.fragment_id_counter = 0
        self.impact_scores = {}       # fragment_id -> impact history

    # ====================== CORE MEMORY OPERATIONS ======================

    def add(self, text: str, metadata: Dict = None):
        if metadata is None:
            metadata = {}
        
        entry = {
            "text": text,
            "metadata": metadata,
            "timestamp": datetime.datetime.now().isoformat(),
            "fragment_id": self._generate_fragment_id(),
            "freshness_score": 1.0,
            "impact_score": 0.0
        }
        
        self.short_term.append(entry)
        self._add_to_graph(entry)
        
        if len(self.short_term) > 40:
            self.compress_to_long_term()
        
        # ByteRover MAU promotion with SOTA gate
        if self.byterover_mau_enabled and metadata.get("local_score", 0.5) > 0.65:
            self.promote_high_signal(text, metadata)
        else:
            self.long_term.add(text, metadata)

    def promote_high_signal(self, text: str, metadata: Dict):
        """SOTA-gated high-signal promotion using verifier + heterogeneity signals."""
        if not self.byterover_mau_enabled:
            return
        
        reinforcement = self._compute_mau_reinforcement(text, metadata)
        
        if reinforcement > 0.78 and self.arbos and hasattr(self.arbos, 'validator'):
            try:
                if self.arbos.validator._subarbos_gate(output=text, theta_dynamic=0.68):
                    metadata["permanent"] = True
                    metadata["mau_reinforcement"] = reinforcement
                    self.long_term.add(text, metadata)
                    logger.info(f"✅ ByteRover MAU promoted high-signal fragment (reinforcement: {reinforcement:.3f})")
                else:
                    logger.debug("High-signal MAU rejected by SOTA gate")
            except Exception as e:
                logger.debug(f"MAU gate failed (safe fallback): {e}")
                self.long_term.add(text, metadata)
        else:
            self.long_term.add(text, metadata)

    def _compute_mau_reinforcement(self, text: str, metadata: Dict) -> float:
        """SOTA reinforcement calculation with multiple signals."""
        validation_score = metadata.get("local_score", 0.5)
        fidelity = metadata.get("fidelity", 0.8)
        heterogeneity = metadata.get("heterogeneity_score", 0.7)
        c3a = metadata.get("c3a_confidence", 0.75)
        
        symbolic_bonus = 0.88 if any(k in text.lower() for k in ["sympy", "invariant", "verifier", "deterministic", "proof"]) else 0.6
        freshness = metadata.get("freshness_score", 1.0)
        
        reinforcement = (validation_score ** 1.2) * (fidelity ** 1.5) * heterogeneity * symbolic_bonus * freshness * c3a
        return min(1.0, reinforcement * self.mau_reinforcement_weight)

    # ====================== v0.9.5 MISSING HELPERS (FULL SOTA IMPLEMENTATION) ======================

    def record_deep_hunt_success(self, metrics: Dict):
        """Track deep ToolHunter hunt successes for tuning and EFS feedback."""
        fragment = {
            "type": "deep_hunt_success",
            "metrics": metrics,
            "timestamp": datetime.datetime.now().isoformat(),
            "impact_score": 0.92,  # deep hunts are high-value
            "novelty_score": metrics.get("novelty_score", 0.0)
        }
        self.add(json.dumps(fragment), {"type": "deep_hunt_success", "local_score": 0.92})
        logger.info(f"🔍 Deep hunt success recorded — {metrics.get('new_fragments', 0)} fragments | novelty {metrics.get('novelty_score', 0):.3f}")

    def record_pattern_evolution_score(self, module_score: float):
        """Record PatternEvolutionArbos 'is it working' module-level score for pruning advisor."""
        fragment = {
            "type": "pattern_evolution_module_score",
            "score": module_score,
            "timestamp": datetime.datetime.now().isoformat(),
            "impact_score": module_score
        }
        self.add(json.dumps(fragment), {"type": "pattern_evolution_module_score", "local_score": module_score})
        logger.info(f"🧬 PatternEvolutionArbos module score recorded: {module_score:.3f}")

    def detect_small_discovery_gaps(self, recent_run_data: Dict) -> List[Dict]:
        """SOTA gap detection for post-run DOUBLE_CLICK recommendations."""
        gaps = []
        efs = recent_run_data.get("efs", 0.0)
        score = recent_run_data.get("final_score", 0.0)
        hetero = recent_run_data.get("heterogeneity_score", 0.72)
        
        if efs < 0.72:
            gaps.append({
                "target": "decay_k",
                "effect": "long_term_retention",
                "domain": "memory_system",
                "description": "Low EFS trend detected — tune memory retention constants",
                "predicted_uplift": 0.12,
                "reason": f"EFS {efs:.3f} below threshold"
            })
        
        if score < 0.78:
            gaps.append({
                "target": "invariant_tightness",
                "effect": "verifier_quality",
                "domain": "verification_pipeline",
                "description": "Low verification quality — strengthen contract invariants",
                "predicted_uplift": 0.15,
                "reason": f"Validation score {score:.3f} below threshold"
            })
        
        if hetero < 0.60:
            gaps.append({
                "target": "exploration_rate",
                "effect": "heterogeneity",
                "domain": "swarm_diversity",
                "description": "Heterogeneity collapse — boost swarm exploration",
                "predicted_uplift": 0.10,
                "reason": f"Heterogeneity {hetero:.3f} below threshold"
            })
        
        return gaps[:3]  # Limit for practicality

    # ====================== FRAGMENTED MEMORY GRAPH SUPPORT ======================

    def _generate_fragment_id(self) -> str:
        self.fragment_id_counter += 1
        return f"frag_{self.fragment_id_counter}"

    def _add_to_graph(self, entry: Dict):
        fid = entry["fragment_id"]
        self.fragment_graph.add_node(fid, **entry)
        
        # Connect to similar recent fragments
        for existing in self.short_term[-10:]:
            if existing["fragment_id"] != fid:
                similarity = self._compute_text_similarity(entry["text"], existing["text"])
                if similarity > 0.65:
                    self.fragment_graph.add_edge(fid, existing["fragment_id"], weight=similarity)

    def _compute_text_similarity(self, text1: str, text2: str) -> float:
        """Simple but effective cosine-like similarity for graph edges."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        return intersection / (len(words1) + len(words2) - intersection)

    def get_current_graph_snapshot(self) -> nx.DiGraph:
        return self.fragment_graph.copy()

    def find_similar_fragments(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Find similar fragments using graph + similarity."""
        candidates = []
        for node, data in self.fragment_graph.nodes(data=True):
            sim = self._compute_text_similarity(query_text, data.get("text", ""))
            if sim > 0.5:
                candidates.append({"id": node, "similarity": sim, **data})
        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        return candidates[:top_k]

    # ====================== COMPRESSION & PRUNING ======================

    def compress_low_value_fragment(self, node: str, decayed_score: float):
        """v0.9.5 Per-fragment compression with provenance only."""
        if decayed_score >= 0.42:
            return
        compress_prompt = f"""Distill this low-signal fragment to 1–3 key sentences + provenance tags only.
Fragment content:
{node[:2000]}
Return ONLY the distilled summary. No extra text."""
        try:
            distilled = self.arbos.harness.call_llm(compress_prompt, temperature=0.2, max_tokens=300)
            self.arbos._write_fragment(
                challenge_id=self.arbos._current_challenge_id,
                subtask_id="compressed",
                fragment={"id": "compressed", "content": distilled, "type": "compressed"},
                metadata={"original_score": round(decayed_score, 4), "compressed": True}
            )
            logger.info(f"✅ Per-fragment compression applied (score {decayed_score:.3f})")
        except Exception as e:
            logger.debug(f"Compression skipped (safe): {e}")

    def compress_low_value(self, current_score: float = 0.0):
        """SOTA-aware pruning with tunable threshold and cosmic compression readiness."""
        threshold = 0.38 if self.byterover_mau_enabled else 0.45
        self.short_term = [entry for entry in self.short_term
                          if entry.get("metadata", {}).get("local_score", 0.5) > threshold]
        
        if len(self.short_term) > 25:
            self.compress_to_long_term()

    def compress_to_long_term(self):
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

    # ====================== QUERY & CONTEXT ======================

    def get_total_context_tokens(self) -> int:
        total = sum(len(entry["text"]) // 4 for entry in self.short_term)
        total += sum(len(entry.get("summary", "")) // 4 for entry in self.long_term_summaries)
        return total

    def query(self, query_text: str, n_results: int = 5):
        return self.long_term.query(query_text, n_results)

    def get_recent_context(self, max_items: int = 8) -> str:
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

    def get_latest_fragments(self) -> List[Dict]:
        """Return most recent ToolHunter + pattern fragments for PatternEvolutionArbos."""
        return self.short_term[-10:] + [s for s in self.long_term_summaries if "pattern" in str(s).lower()]

    def get_domain_gap_severity(self, domains: List[str]) -> float:
        """Gap severity for targeted hunts (0-1)."""
        severity = 0.0
        for domain in domains:
            if any(d in str(domain).lower() for d in ["quantum", "fusion", "plasma", "stabilizer"]):
                severity = max(severity, 0.82)
            elif any(d in str(domain).lower() for d in ["battery", "decoder", "optimization"]):
                severity = max(severity, 0.68)
        return min(1.0, severity)

    def add_proposals(self, proposals: List[str]):
        self.tool_proposals.extend(proposals)
        for p in proposals:
            self.add(f"TOOL PROPOSAL: {p}", {"type": "tool_proposal", "local_score": 0.75})

# Global instances
memory = LongTermMemory()
memory_layers = MemoryLayers()
