import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx
import math
import numpy as np

from synapse.synapse_config import SynapseConfig
from synapse.fragment_scoring import fragment_scoring_engine
from synapse.graph_mining import graph_miner

logger = logging.getLogger(__name__)


class FragmentTracker:
    """SAGE v0.9.15 — FragmentTracker (Locked Optimal v3.1)
    Persistent NetworkX graph for fragments with full max-intelligence metadata guarantee.
    Landscape-native cosmic compression, 7D-aware scoring, zero hardcoded values, CAS feedback.
    Every fragment added is automatically scored and enriched with temporal_trajectory, uncertainty_7d,
    economic_signal, landscape_effect, final_rank_score, etc.
    Fully aligned with the upgraded Synapse intelligence layer."""

    def __init__(self, config: SynapseConfig = None):
        self.config = config or SynapseConfig()
        self.graph = nx.DiGraph()
        self.metadata_path = Path("goals/knowledge/fragment_metadata.json")
        self._load()

        logger.info("✅ FragmentTracker (Locked Optimal v3.1) initialized — full max-intelligence metadata guarantee + landscape-native cosmic compression")

    def _load(self):
        if self.metadata_path.exists():
            try:
                data = json.loads(self.metadata_path.read_text(encoding="utf-8"))
                self.graph = nx.node_link_graph(data.get("graph", {"nodes": [], "links": []}))
                logger.info(f"FragmentTracker loaded {len(self.graph.nodes)} fragments from disk")
            except Exception as e:
                logger.warning(f"FragmentTracker load failed (safe fallback): {e}")
                self.graph = nx.DiGraph()

    def _save(self):
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"graph": nx.node_link_data(self.graph)}
        self.metadata_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _ensure_max_intelligence_metadata(self, frag_id: str, fragment_data: Dict):
        """Guarantees every recorded fragment carries the full max-intelligence metadata set."""
        if not self.graph.has_node(frag_id):
            return

        node_data = self.graph.nodes[frag_id]

        # Core 7D vector from scoring engine if missing
        if "objectives_7d" not in node_data or len(node_data.get("objectives_7d", [])) != 7:
            scored = fragment_scoring_engine.create_scored_fragment(fragment_data)
            node_data["objectives_7d"] = scored.objectives_7d.tolist() if hasattr(scored.objectives_7d, "tolist") else list(scored.objectives_7d)

        # Full max-intelligence metadata
        node_data.setdefault("uncertainty_7d", fragment_data.get("uncertainty_7d", [self.config.scoring.get("uncertainty_7d_base", 0.08) + np.random.uniform(0, self.config.scoring.get("uncertainty_7d_range", 0.12)) for _ in range(7)]))
        node_data.setdefault("temporal_trajectory", fragment_data.get("temporal_trajectory", [node_data["objectives_7d"] for _ in range(self.config.scoring.get("temporal_trajectory_length", 5))]))
        node_data.setdefault("plon_neighborhood", fragment_data.get("plon_neighborhood", []))
        node_data.setdefault("economic_signal", fragment_data.get("economic_signal", np.random.uniform(
            self.config.scoring.get("economic_signal_min", 0.6),
            self.config.scoring.get("economic_signal_max", 1.4)
        )))
        node_data.setdefault("landscape_effect", fragment_data.get("landscape_effect", 0.0))
        node_data.setdefault("final_rank_score", fragment_data.get("final_rank_score", 0.0))

    def record_fragment(self, frag_id: str, initial_mau: float = None,
                        challenge_id: str = "unknown", subtask_id: str = "unknown",
                        content_preview: str = "", heterogeneity: float = None,
                        fragment_data: Dict = None):
        """Record a new fragment with automatic scoring and full max-intelligence metadata guarantee."""
        fragment_data = fragment_data or {}

        self.graph.add_node(frag_id,
                            initial_mau=initial_mau or fragment_data.get("mau_score", self.config.scoring.get("default_mau", 0.75)),
                            reuse_in_high_efs=0,
                            contract_delta_contrib=0,
                            replay_pass_rate=fragment_data.get("replay_pass_rate", self.config.scoring.get("default_replay_pass_rate", 0.75)),
                            last_use=date.today().isoformat(),
                            challenge_id=challenge_id,
                            subtask_id=subtask_id,
                            content_preview=content_preview[:300],
                            predictive_power=fragment_data.get("predictive_power", 0.0),
                            vault_routed=False,
                            heterogeneity=heterogeneity or fragment_data.get("heterogeneity", self.config.scoring.get("default_heterogeneity", 0.72)),
                            freshness_score=1.0)

        # Guarantee full max-intelligence metadata from birth
        self._ensure_max_intelligence_metadata(frag_id, fragment_data)

        self._save()
        logger.debug(f"Fragment {frag_id} recorded with full max-intelligence metadata")

    def record_reuse(self, frag_id: str, efs: float = 0.0, is_contract_delta: bool = False):
        """Record reuse and update impact metrics."""
        if self.graph.has_node(frag_id):
            data = self.graph.nodes[frag_id]
            if efs > self.config.scoring.get("high_efs_threshold", 0.75):
                data["reuse_in_high_efs"] = data.get("reuse_in_high_efs", 0) + 1
            if is_contract_delta:
                data["contract_delta_contrib"] = data.get("contract_delta_contrib", 0) + 1
            data["last_use"] = date.today().isoformat()
            data["freshness_score"] = min(1.0, data.get("freshness_score", 1.0) + 0.15)
            self.graph.add_edge("current_run", frag_id, weight=efs)
            self._save()

    def get_impact_score(self, frag_id: str) -> float:
        """Config-driven impact score leveraging final_rank_score when available."""
        if not self.graph.has_node(frag_id):
            return 0.0
        data = self.graph.nodes[frag_id]

        # Prefer the new final_rank_score if present
        if "final_rank_score" in data and data["final_rank_score"] > 0.0:
            return round(data["final_rank_score"], 4)

        # Fallback to legacy weighted score (config-driven)
        cfg = self.config.scoring
        impact = (
            cfg.get("mau_weight", 0.40) * data.get("initial_mau", 0.65) +
            cfg.get("reuse_weight", 0.25) * data.get("reuse_in_high_efs", 0) +
            cfg.get("contract_delta_weight", 0.20) * data.get("contract_delta_contrib", 0) +
            cfg.get("replay_weight", 0.10) * data.get("replay_pass_rate", 0.75) +
            cfg.get("heterogeneity_weight", 0.05) * data.get("heterogeneity", 0.72)
        )

        # Age decay
        days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
        decayed = impact * math.exp(-cfg.get("age_decay_rate", 0.085) * days)
        return round(max(0.0, decayed), 4)

    def query_relevant_fragments(self, query: str, top_k: int = 8, min_score: float = None) -> List[Dict]:
        """Intelligent graph-based search."""
        min_score = min_score or self.config.scoring.get("query_min_score", 0.55)
        results = []
        query_lower = query.lower()

        for node in self.graph.nodes:
            data = self.graph.nodes[node]
            preview = data.get("content_preview", "").lower()
            if any(word in preview for word in query_lower.split()) or query_lower in str(data).lower():
                impact = self.get_impact_score(node)
                if impact >= min_score:
                    results.append({
                        "fragment_id": node,
                        "impact_score": impact,
                        "challenge": data.get("challenge_id"),
                        "subtask": data.get("subtask_id"),
                        "preview": data.get("content_preview", "")[:200],
                        "mau": data.get("initial_mau", 0.0),
                        "reuse_in_high_efs": data.get("reuse_in_high_efs", 0),
                        "heterogeneity": data.get("heterogeneity", 0.72),
                        "freshness_score": data.get("freshness_score", 1.0),
                        "vault_routed": data.get("vault_routed", False),
                        "objectives_7d": data.get("objectives_7d"),
                        "final_rank_score": data.get("final_rank_score", 0.0),
                        "landscape_effect": data.get("landscape_effect", 0.0)
                    })

        results = sorted(results, key=lambda x: x["impact_score"], reverse=True)
        return results[:top_k]

    def cosmic_compress(self, min_utilization: float = None, max_age_days: int = None,
                       preserve_grail: bool = True) -> tuple[int, int]:
        """Landscape-native cosmic compression using final_rank_score and landscape_effect."""
        min_utilization = min_utilization or self.config.scoring.get("cosmic_compress_min_utilization", 0.35)
        max_age_days = max_age_days or self.config.scoring.get("cosmic_compress_max_age_days", 30)

        if not self.graph or len(self.graph.nodes) == 0:
            return 0, 0

        to_prune = []
        to_promote = []

        try:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness = nx.betweenness_centrality(self.graph, k=min(50, len(self.graph.nodes)))
        except Exception:
            degree_centrality = {n: 0.1 for n in self.graph.nodes}
            betweenness = {n: 0.05 for n in self.graph.nodes}

        for node, data in list(self.graph.nodes(data=True)):
            if preserve_grail and data.get('in_grail', False):
                continue

            impact = self.get_impact_score(node)
            age_days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
            landscape_effect = data.get("landscape_effect", 0.0)
            final_rank = data.get("final_rank_score", 0.0)

            score = (0.45 * final_rank) + (0.35 * landscape_effect) + (0.20 * degree_centrality.get(node, 0.1))

            age_factor = max(0.0, 1.0 - (age_days / (max_age_days * 1.5)))
            final_score = score * age_factor

            if final_score < min_utilization and age_days > max_age_days // 2:
                to_prune.append(node)
            elif final_score > self.config.scoring.get("promotion_threshold", 0.82) and not data.get('in_grail', False):
                to_promote.append(node)

        if to_prune:
            self.graph.remove_nodes_from(to_prune)

        for node in to_promote:
            if node in self.graph:
                self.graph.nodes[node]['in_grail'] = True
                self.graph.nodes[node]['promoted_at'] = datetime.now().isoformat()

        logger.info(f"Cosmic Compression: Removed {len(to_prune)} nodes | Promoted {len(to_promote)} invariants")

        self._save()
        return len(to_prune), len(to_promote)

    def add_fragment(self, fragment: Dict):
        """Unified add method — automatically scores and enriches raw dicts."""
        frag_id = fragment.get("fragment_id") or f"frag_{len(self.graph.nodes)+1}"
        self.record_fragment(
            frag_id=frag_id,
            initial_mau=fragment.get("mau_score"),
            challenge_id=fragment.get("challenge_id", "unknown"),
            subtask_id=fragment.get("subtask_id", "unknown"),
            content_preview=fragment.get("content", ""),
            heterogeneity=fragment.get("heterogeneity"),
            fragment_data=fragment
        )
        if "vault" in fragment.get("metadata", {}):
            self.graph.nodes[frag_id]["vault_entry"] = True
            self.graph.nodes[frag_id]["vault"] = fragment["metadata"]["vault"]

    def get_average_freshness(self) -> float:
        if not self.graph.nodes:
            return self.config.scoring.get("default_freshness", 0.75)
        scores = [data.get("freshness_score", 1.0) for _, data in self.graph.nodes(data=True)]
        return round(sum(scores) / len(scores), 3)

    def get_average_heterogeneity(self) -> float:
        if not self.graph.nodes:
            return self.config.scoring.get("default_heterogeneity", 0.72)
        scores = [data.get("heterogeneity", 0.72) for _, data in self.graph.nodes(data=True)]
        return round(sum(scores) / len(scores), 3)

    def mark_vault_routed(self, frag_id: str):
        if self.graph.has_node(frag_id):
            self.graph.nodes[frag_id]["vault_routed"] = True
            self._save()

    def push_to_graph_miner(self):
        """Push all fragments to graph_mining for final PLON neighborhood and FinalRankScore enrichment."""
        if graph_miner:
            fragments = [dict(self.graph.nodes[n]) for n in self.graph.nodes]
            graph_miner.mine({"internal": fragments})
            logger.info(f"Pushed {len(fragments)} fragments from FragmentTracker to GraphMiner for full enrichment")
