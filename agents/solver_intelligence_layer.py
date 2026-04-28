import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SolverIntelligenceLayer:
    """SOTA SolverIntelligenceLayer — Graph-integrated VaultRouter with explicit fragment scoring, 7D signals, and full flywheel routing."""

    def __init__(self, memory_layers=None, fragment_tracker=None):
        self.memory = memory_layers
        self.fragment_tracker = fragment_tracker
        self.vault_root = Path("vaults")
        self.vault_root.mkdir(parents=True, exist_ok=True)
       
        self.vaults = {}
        for vault in ["publications", "assets", "services", "academy"]:
            vault_dir = self.vault_root / vault
            vault_dir.mkdir(exist_ok=True)
            self.vaults[vault] = vault_dir
       
        self.stats = {"publications": 0, "assets": 0, "services": 0, "academy": 0}
        logger.info("🚀 SolverIntelligenceLayer v0.9.13+ SOTA — full graph-integrated VaultRouter active")

    def _calculate_vault_scores(self, run_data: Dict) -> Dict:
        """Maximum intelligence scoring using predictive, EFS, freshness, heterogeneity, MAU, and 7D signals."""
        insight = run_data.get("insight_score", 0.0)
        predictive = run_data.get("predictive_power", 0.0)
        efs = run_data.get("efs", 0.0)
        freshness = run_data.get("freshness_avg", 0.7)
        heterogeneity = run_data.get("heterogeneity", 0.0)
        mau = run_data.get("mau_score", 0.0)
        verifier_quality = run_data.get("verifier_quality", 0.0)

        return {
            "publications": min(1.0, insight * 0.45 + predictive * 0.35 + freshness * 0.2 + verifier_quality * 0.1),
            "assets": min(1.0, efs * 0.5 + predictive * 0.3 + heterogeneity * 0.2 + verifier_quality * 0.1),
            "services": min(1.0, predictive * 0.55 + insight * 0.3 + freshness * 0.15 + verifier_quality * 0.1),
            "academy": min(1.0, insight * 0.5 + efs * 0.3 + freshness * 0.2 + verifier_quality * 0.15)
        }

    def route_to_vaults(self, run_data: Dict):
        """SOTA VaultRouter — appends to files AND integrates into the main fragmented graph with explicit scoring."""
        insight = self.distill_run_insight(run_data)
        scores = self._calculate_vault_scores(run_data)
        timestamp = datetime.now().isoformat()
        routed = []

        fragment_metadata = {
            "type": "vault_entry",
            "run_id": run_data.get("loop", "unknown"),
            "score": run_data.get("final_score", 0.0),
            "efs": run_data.get("efs", 0.0),
            "predictive_power": run_data.get("predictive_power", 0.0),
            "verifier_quality": run_data.get("verifier_quality", 0.0),
            "timestamp": timestamp
        }

        if scores["publications"] > 0.82:
            self._append_to_vault("publications", insight, run_data, timestamp)
            routed.append("publications")
            if self.fragment_tracker and hasattr(self.fragment_tracker, 'add_fragment'):
                self.fragment_tracker.add_fragment({
                    "content": insight,
                    "metadata": {**fragment_metadata, "vault": "publications"}
                })

        if scores["assets"] > 0.80:
            self._append_to_vault("assets", insight, run_data, timestamp)
            routed.append("assets")
            if self.fragment_tracker and hasattr(self.fragment_tracker, 'add_fragment'):
                self.fragment_tracker.add_fragment({
                    "content": insight,
                    "metadata": {**fragment_metadata, "vault": "assets"}
                })

        if scores["services"] > 0.78:
            self._append_to_vault("services", insight, run_data, timestamp)
            routed.append("services")
            if self.fragment_tracker and hasattr(self.fragment_tracker, 'add_fragment'):
                self.fragment_tracker.add_fragment({
                    "content": insight,
                    "metadata": {**fragment_metadata, "vault": "services"}
                })

        if scores["academy"] > 0.88:
            self._append_to_vault("academy", insight, run_data, timestamp, crown_jewel=True)
            routed.append("academy")
            if self.fragment_tracker and hasattr(self.fragment_tracker, 'add_fragment'):
                self.fragment_tracker.add_fragment({
                    "content": insight,
                    "metadata": {**fragment_metadata, "vault": "academy", "crown_jewel": True}
                })

        logger.info(f"VaultRouter routed + graph-integrated — {routed} | Scores: { {k: round(v, 3) for k, v in scores.items()} }")

    def _append_to_vault(self, vault_name: str, insight: str, run_data: Dict, timestamp: str, crown_jewel: bool = False):
        """Pure append-only with rich provenance and explicit scoring."""
        vault_dir = self.vaults.get(vault_name)
        if not vault_dir:
            return

        filename = f"{timestamp.replace(':', '-')}.md"
        path = vault_dir / filename

        content = f"""# {vault_name.capitalize()} Entry — {timestamp}
**Insight Score**: {run_data.get('insight_score', 'N/A')}
**Predictive Power**: {run_data.get('predictive_power', 'N/A')}
**EFS**: {run_data.get('efs', 'N/A')}
**Freshness**: {run_data.get('freshness_avg', 'N/A')}
**Heterogeneity**: {run_data.get('heterogeneity', 'N/A')}
**Verifier Quality (7D)**: {run_data.get('verifier_quality', 'N/A')}
**Provenance**: Enigma Miner Run {run_data.get('loop', 'unknown')} | Crown Jewel: {crown_jewel}

{insight}

**Source Data**:
```json
{json.dumps({k: v for k, v in run_data.items() if k in ['validation_score', 'predictive_power', 'final_score', 'efs', 'heterogeneity', 'verifier_quality']}, indent=2)}
```"""

        path.write_text(content, encoding="utf-8")
        self.stats[vault_name] += 1

    def distill_run_insight(self, run_data: Dict) -> str:
        """SOTA insight distillation with key metrics and takeaways."""
        return f"""High-signal run completed at {datetime.now().strftime('%Y-%m-%d %H:%M')}.

Validation Score: {run_data.get('final_score', run_data.get('validation_score', 'N/A'))}
EFS: {run_data.get('efs', 'N/A')}
Predictive Power: {run_data.get('predictive_power', 'N/A')}
Heterogeneity: {run_data.get('heterogeneity', 'N/A')}
Verifier Quality (7D): {run_data.get('verifier_quality', 'N/A')}

Key Takeaway: Strong, verifiable process data suitable for open public good accumulation and human education."""

    def get_vault_stats(self) -> Dict:
        """Live statistics for Streamlit dashboard."""
        total = sum(self.stats.values())
        return {
            "total_entries": total,
            "publications": self.stats["publications"],
            "assets": self.stats["assets"],
            "services": self.stats["services"],
            "academy": self.stats["academy"],
            "last_updated": datetime.now().isoformat()
        }
