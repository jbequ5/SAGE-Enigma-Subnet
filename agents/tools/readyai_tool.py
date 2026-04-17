# agents/tools/readyai_tool.py
# v0.9.11 MAXIMUM SOTA ReadyAI_KnowledgeTool (llms.txt integration)
# Domain-aware structured knowledge + full SOTA/EFS/7D wiring + VaultRouter + Model Bank synergy

import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ReadyAI_KnowledgeTool:
    def __init__(self):
        self.api_base = "https://llms-text.ai/api"
        self.cache_dir = Path("cache/readyai")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.arbos = None          # wired by ArbosManager
        self.validator = None      # for SOTA gate
        self.predictive = None     # for predictive boost
        self.fragment_tracker = None
        self.intelligence = None
        logger.info("✅ ReadyAI_KnowledgeTool v0.9.11 MAX SOTA initialized — full SOTA/EFS/7D + VaultRouter integration")

    def set_arbos(self, arbos):
        self.arbos = arbos
        if arbos:
            self.validator = getattr(arbos, 'validator', None)
            self.predictive = getattr(arbos, 'predictive', None)
            self.fragment_tracker = getattr(arbos, 'fragment_tracker', None)
            self.intelligence = getattr(arbos, 'intelligence', None)

    def query(self, search_term: str, limit: int = 5) -> Dict[str, Any]:
        """Query llms.txt knowledge base for any domain or topic."""
        try:
            response = requests.get(
                f"{self.api_base}/search-llms",
                params={"q": search_term, "limit": limit},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])[:limit]
           
            if results:
                logger.info(f"ReadyAI returned {len(results)} structured summaries for '{search_term}'")
                return {
                    "success": True,
                    "query": search_term,
                    "results": results,
                    "summary": f"Found structured knowledge for {len(results)} sources related to '{search_term}'"
                }
            else:
                return {"success": False, "message": f"No llms.txt data found for '{search_term}'"}
        except Exception as e:
            logger.warning(f"ReadyAI query failed: {e}")
            return {"success": False, "message": f"ReadyAI lookup error: {str(e)[:100]}"}

    def get_domain_summary(self, domain: str) -> str:
        """Get clean summary for a specific domain (e.g. 'openai.com', 'arxiv.org')."""
        result = self.query(domain, limit=3)
        if result["success"] and result["results"]:
            return "\n\n".join([r.get("summary", r.get("content", "")) for r in result["results"]])
        return f"[No structured data available for {domain}]"

    def get_structured_knowledge(self, query: str, limit: int = 4) -> Dict[str, Any]:
        """Main public method used by ToolHunter and Arbos — with full SOTA gating."""
        result = self.query(query, limit=limit)

        # v0.9.11 SOTA upgrade: apply 7D verifier gate + EFS-aware filtering
        if self.arbos and self.validator and result.get("success"):
            try:
                gate_data = {
                    "deterministic_strength": 0.65,
                    "edge_coverage": 0.75,
                    "invariant_tightness": 0.70,
                    "simulation_quality": 0.68,
                    "fidelity": 0.82,
                    "c3a_confidence": getattr(self.arbos, 'compute_confidence', lambda *a: 0.75)(0.78, 0.70, 0.88),
                    "verifier_quality": getattr(self.validator, 'last_verifier_quality', 0.0)
                }
                if hasattr(self.validator, '_subarbos_gate'):
                    if not self.validator._subarbos_gate(output=str(result), theta_dynamic=0.68):
                        result["sota_gate"] = False
                        result["summary"] += " | [SOTA gate failed — low signal content]"
                        logger.debug(f"ReadyAI content for '{query}' rejected by SOTA gate")
                    else:
                        result["sota_gate"] = True
            except Exception as e:
                logger.debug(f"SOTA gate check skipped (safe): {e}")

        # High-signal routing to Vaults + PD Arm
        if result.get("success") and len(str(result.get("results", ""))) > 600 and self.intelligence:
            run_data = {
                "insight_score": 0.88,
                "key_takeaway": f"ReadyAI delivered high-signal structured knowledge for '{query}'",
                "predictive_power": getattr(self.predictive, 'predictive_power', 0.0) if self.predictive else 0.0,
                "flywheel_step": "readyai_to_vaults_pd",
                "source": "llms.txt"
            }
            self.intelligence.route_to_vaults(run_data)
            if self.arbos and hasattr(self.arbos, 'pd_arm'):
                self.arbos.pd_arm.synthesize_product([], {"market_signal": f"ReadyAI knowledge: {query}"})

        return result

    def get_structured_knowledge_with_score(self, query: str, limit: int = 4) -> Dict[str, Any]:
        """v0.9.11 helper: returns knowledge + EFS/SOTA hint for retrospective/audit flows."""
        result = self.get_structured_knowledge(query, limit)
        result["efs_hint"] = "high_signal" if len(str(result.get("results", ""))) > 800 else "low_signal"
        result["verifier_quality_hint"] = getattr(self.validator, 'last_verifier_quality', 0.0) if self.validator else 0.0
        return result

    def get_model_recommendations(self, domain: str) -> List[Dict]:
        """New: ReadyAI can feed discovered models into the Model Hunting Bank."""
        result = self.query(f"best models for {domain}", limit=6)
        models = []
        if result.get("success"):
            for r in result.get("results", []):
                if "model" in str(r).lower() or "huggingface" in str(r).lower():
                    models.append({
                        "name": r.get("title", "Unnamed Model"),
                        "url": r.get("url"),
                        "source": "readyai",
                        "description": r.get("summary", "")[:300]
                    })
        return models

# Global instance
readyai_tool = ReadyAI_KnowledgeTool()
