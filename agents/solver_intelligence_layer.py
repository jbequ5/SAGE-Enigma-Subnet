# agents/solver_intelligence_layer.py - v0.9.7 MAXIMUM SOTA VaultRouter + 4 Open Public Good Vaults
# Intelligent scoring, rich provenance, auto-summarization, statistics tracking, and full integration.

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SolverIntelligenceLayer:
    def __init__(self, memory_layers=None):
        self.memory = memory_layers
        self.vault_root = Path("vaults")
        self.vault_root.mkdir(parents=True, exist_ok=True)
        
        # Create the 4 append-only vaults
        self.vaults = {}
        for vault in ["publications", "assets", "services", "academy"]:
            vault_dir = self.vault_root / vault
            vault_dir.mkdir(exist_ok=True)
            self.vaults[vault] = vault_dir

        # Statistics tracking
        self.stats = {"publications": 0, "assets": 0, "services": 0, "academy": 0}

    def _calculate_vault_scores(self, run_data: Dict) -> Dict:
        """Maximum intelligence scoring using predictive, EFS, freshness, and heterogeneity."""
        insight = run_data.get("insight_score", 0.0)
        predictive = run_data.get("predictive_power", 0.0)
        efs = run_data.get("efs", 0.0)
        freshness = run_data.get("freshness_avg", 0.7)
        heterogeneity = run_data.get("heterogeneity", 0.0)

        return {
            "publications": min(1.0, insight * 0.45 + predictive * 0.35 + freshness * 0.2),
            "assets": min(1.0, efs * 0.5 + predictive * 0.3 + heterogeneity * 0.2),
            "services": min(1.0, predictive * 0.55 + insight * 0.3 + freshness * 0.15),
            "academy": min(1.0, insight * 0.5 + efs * 0.3 + freshness * 0.2)  # Crown jewel bias
        }

    def route_to_vaults(self, run_data: Dict):
        """SOTA VaultRouter — intelligent routing with provenance and statistics."""
        insight = self.distill_run_insight(run_data)
        scores = self._calculate_vault_scores(run_data)
        timestamp = datetime.now().isoformat()

        routed = []
        if scores["publications"] > 0.82:
            self._append_to_vault("publications", insight, run_data, timestamp)
            routed.append("publications")
        if scores["assets"] > 0.80:
            self._append_to_vault("assets", insight, run_data, timestamp)
            routed.append("assets")
        if scores["services"] > 0.78:
            self._append_to_vault("services", insight, run_data, timestamp)
            routed.append("services")
        if scores["academy"] > 0.88:
            self._append_to_vault("academy", insight, run_data, timestamp, crown_jewel=True)
            routed.append("academy")

        logger.info(f"VaultRouter routed to: {routed} | Scores: { {k: round(v,3) for k,v in scores.items()} }")

    def _append_to_vault(self, vault_name: str, insight: str, run_data: Dict, timestamp: str, crown_jewel: bool = False):
        """Pure append-only with rich provenance and metadata."""
        vault_dir = self.vaults[vault_name]
        filename = f"{timestamp.replace(':', '-')}.md"
        path = vault_dir / filename

        content = f"""# {vault_name.capitalize()} Entry — {timestamp}

**Insight Score**: {run_data.get('insight_score', 'N/A')}
**Predictive Power**: {run_data.get('predictive_power', 'N/A')}
**EFS**: {run_data.get('efs', 'N/A')}
**Freshness**: {run_data.get('freshness_avg', 'N/A')}
**Provenance**: Enigma Miner Run {run_data.get('loop', 'unknown')} | Crown Jewel: {crown_jewel}

{insight}

**Source Data**:
```json
{json.dumps({k: v for k, v in run_data.items() if k in ['validation_score', 'predictive_power', 'final_score', 'efs', 'heterogeneity']}, indent=2)}
      """    path.write_text(content, encoding="utf-8")
    self.stats[vault_name] += 1
    logger.debug(f"Appended to {vault_name} vault: {filename}")

def distill_run_insight(self, run_data: Dict) -> str:
    """SOTA insight distillation with key metrics and takeaways."""
    return f"""High-signal run completed at {datetime.now().strftime('%Y-%m-%d %H:%M')}.Validation Score: {run_data.get('final_score', run_data.get('validation_score', 'N/A'))}
EFS: {run_data.get('efs', 'N/A')}
Predictive Power: {run_data.get('predictive_power', 'N/A')}
Heterogeneity: {run_data.get('heterogeneity', 'N/A')}Key Takeaway: Strong, verifiable process data suitable for open public good accumulation and human education."""def get_vault_stats(self) -> Dict:
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

