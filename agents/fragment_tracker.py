# agents/fragment_tracker.py
import json
import math
from pathlib import Path
from datetime import date
import networkx as nx

class FragmentTracker:
    """Persistent fragment metadata + NetworkX graph for v0.8+ Wiki Memory Strategy."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.metadata_path = Path("goals/knowledge/fragment_metadata.json")
        self._load()

    def _load(self):
        if self.metadata_path.exists():
            try:
                data = json.loads(self.metadata_path.read_text(encoding="utf-8"))
                self.graph = nx.node_link_graph(data.get("graph", {"nodes": [], "links": []}))
            except:
                pass

    def _save(self):
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"graph": nx.node_link_data(self.graph)}
        self.metadata_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def record_fragment(self, frag_id: str, initial_mau: float, challenge_id: str, subtask_id: str, content_preview: str = ""):
        self.graph.add_node(frag_id, 
                            initial_mau=initial_mau,
                            reuse_in_high_efs=0,
                            contract_delta_contrib=0,
                            replay_pass_rate=0.75,
                            last_use=date.today().isoformat(),
                            challenge_id=challenge_id,
                            subtask_id=subtask_id,
                            content_preview=content_preview[:300])
        self._save()

    def record_reuse(self, frag_id: str, efs: float, is_contract_delta: bool = False):
        """Record reuse and optionally mark as contract-related."""
        if self.graph.has_node(frag_id):
            data = self.graph.nodes[frag_id]
            if efs > 0.75:
                data["reuse_in_high_efs"] = data.get("reuse_in_high_efs", 0) + 1
            if is_contract_delta:
                data["contract_delta_contrib"] = data.get("contract_delta_contrib", 0) + 1
            data["last_use"] = date.today().isoformat()
            self.graph.add_edge("current_run", frag_id, weight=efs)
            self._save()

    def get_impact_score(self, frag_id: str) -> float:
        if not self.graph.has_node(frag_id):
            return 0.0
        data = self.graph.nodes[frag_id]
        impact = (0.4 * data.get("initial_mau", 0.65)) + \
                 (0.3 * data.get("reuse_in_high_efs", 0)) + \
                 (0.2 * data.get("contract_delta_contrib", 0)) + \
                 (0.1 * data.get("replay_pass_rate", 0.75))
        
        days = (date.today() - date.fromisoformat(data.get("last_use", "2025-01-01"))).days
        decayed = impact * math.exp(-0.08 * days)
        return round(decayed, 4)

    def query_relevant_fragments(self, query: str, top_k: int = 5) -> list:
        """Intelligent graph search for Orchestrator, Synthesis, Symbiosis, ToolHunter."""
        results = []
        for node in self.graph.nodes:
            data = self.graph.nodes[node]
            preview = data.get("content_preview", "")
            if any(word.lower() in preview.lower() for word in query.lower().split()):
                score = self.get_impact_score(node)
                results.append({
                    "fragment_id": node,
                    "impact_score": score,
                    "challenge": data.get("challenge_id"),
                    "subtask": data.get("subtask_id"),
                    "preview": preview[:150]
                })
        return sorted(results, key=lambda x: x["impact_score"], reverse=True)[:top_k]

    def cosmic_compress(self, min_utilization: float = 0.35, max_age_days: int = 30, 
                       preserve_grail: bool = True) -> Tuple[int, int]:
        """v0.9+ Advanced Cosmic Compression with multi-criteria scoring, 
        centrality, and community awareness."""
        
        if not self.graph or len(self.graph.nodes) == 0:
            return 0, 0

        to_prune = []
        to_promote = []
        
        # Calculate graph metrics once
        try:
            degree_centrality = nx.degree_centrality(self.graph)
            betweenness = nx.betweenness_centrality(self.graph, k=min(50, len(self.graph.nodes)))
        except:
            degree_centrality = {n: 0.1 for n in self.graph.nodes}
            betweenness = {n: 0.05 for n in self.graph.nodes}

        for node, data in list(self.graph.nodes(data=True)):
            # Skip protected nodes
            if preserve_grail and data.get('in_grail', False):
                continue

            mau = data.get('mau', 0.0)
            impact = data.get('impact_score', 0.0)
            reuse = data.get('reuse_count', 0)
            age_days = data.get('age_days', 0)
            in_high_efs = data.get('in_high_efs_run', False)

            # Multi-criteria score
            score = (
                0.35 * mau +
                0.25 * impact +
                0.15 * (reuse * 0.1) +           # reuse bonus
                0.10 * degree_centrality.get(node, 0.1) +
                0.08 * betweenness.get(node, 0.05) +
                0.07 * (1.0 if in_high_efs else 0.3)
            )

            # Age penalty (Ebbinghaus-style)
            age_factor = max(0.0, 1.0 - (age_days / (max_age_days * 1.5)))
            final_score = score * age_factor

            if final_score < min_utilization and age_days > max_age_days // 2:
                to_prune.append(node)
            elif final_score > 0.82 and not data.get('in_grail', False):
                to_promote.append(node)

        # Execute pruning and promotion
        if to_prune:
            self.graph.remove_nodes_from(to_prune)
            
        for node in to_promote:
            if node in self.graph:
                self.graph.nodes[node]['in_grail'] = True
                self.graph.nodes[node]['promoted_at'] = datetime.now().isoformat()

        logger.info(f"Cosmic Compression: Removed {len(to_prune)} nodes | Promoted {len(to_promote)} invariants")
        
        return len(to_prune), len(to_promote)
