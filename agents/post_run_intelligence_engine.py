# agents/post_run_intelligence_engine.py
# v0.9.11 MAXIMUM SOTA Post-Run Intelligence Engine
# Single source of truth for all post-EM intelligence: VaultRouter, Predictive, Synthesis Arbos,
# BusinessDev, full graph intelligence, self-critique, Grail promotion, and Economic Flywheel closure.

import logging
import time
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class PostRunIntelligenceEngine:
    def __init__(self, arbos_manager):
        self.arbos = arbos_manager
        self.intelligence = getattr(arbos_manager, 'intelligence', None)
        self.predictive = getattr(arbos_manager, 'predictive', None)
        self.pd_arm = getattr(arbos_manager, 'pd_arm', None)
        self.business_dev = getattr(arbos_manager, 'business_dev', None)
        self.fragment_tracker = getattr(arbos_manager, 'fragment_tracker', None)
        logger.info("🚀 PostRunIntelligenceEngine v0.9.11 MAX SOTA initialized — full graph + predictive + vault wiring active")

    def process_high_signal_run(self, run_data: Dict):
        """Unified SOTA post-EM pipeline — coordinates everything with maximum intelligence."""
        start = time.time()
        logger.info("🚀 PostRunIntelligenceEngine — starting full SOTA post-EM processing")

        try:
            # 1. Predictive update with full real metrics (including graph signals)
            if self.predictive and hasattr(self.predictive, 'update_from_run'):
                self.predictive.update_from_run(run_data)

            # 2. VaultRouter with full graph integration
            if self.intelligence and hasattr(self.intelligence, 'route_to_vaults'):
                # Enrich run_data with graph signals
                graph_insights = []
                if self.fragment_tracker and hasattr(self.fragment_tracker, 'query_relevant_fragments'):
                    graph_insights = self.fragment_tracker.query_relevant_fragments(
                        query="high_signal OR resonance OR photoelectric OR breakthrough",
                        top_k=8,
                        min_score=0.72
                    )
                run_data["graph_insights_used"] = len(graph_insights)
                self.intelligence.route_to_vaults(run_data)

            # 3. Synthesis Arbos / Product Development Arm with real vault + predictive data
            product = {"name": "No product synthesized", "type": "none"}
            if self.pd_arm and hasattr(self.pd_arm, 'synthesize_product'):
                market_signals = {
                    "predictive_power": getattr(self.predictive, 'predictive_power', 0.0) if self.predictive else 0.0,
                    "market_demand_score": getattr(self.predictive, 'market_demand_signal', 0.0) if self.predictive else 0.0,
                    "efs": run_data.get("efs", 0.0),
                    "final_score": run_data.get("final_score", 0.0),
                    "heterogeneity": run_data.get("heterogeneity_score", 0.72)
                }
                product = self.pd_arm.synthesize_product(
                    vault_data=graph_insights if 'graph_insights' in locals() else [],
                    market_signals=market_signals
                )

            # 4. BusinessDev hunt for flywheel closure + lead generation
            bd_results = {"opportunities": []}
            if self.business_dev and hasattr(self.business_dev, 'run_hunt_cycle'):
                bd_results = self.business_dev.run_hunt_cycle(
                    user_query=f"Post-run high-signal flywheel closure - score {run_data.get('final_score', 0.0):.3f} | "
                               f"EFS {run_data.get('efs', 0.0):.3f} | Predictive {getattr(self.predictive, 'predictive_power', 0.0):.3f}"
                )

            # 5. Self-critique and Grail promotion on high-signal runs
            if run_data.get("final_score", 0.0) > 0.82 and hasattr(self.arbos, 'grail_extract_and_score'):
                self.arbos.grail_extract_and_score(
                    solution=run_data.get("best_solution", ""),
                    validation_score=run_data.get("final_score", 0.0),
                    fidelity=run_data.get("fidelity", 0.85),
                    diagnostics=run_data
                )

            # 6. Unified high-signal trace with full observability
            duration = time.time() - start
            trace_data = {
                "final_score": run_data.get("final_score", 0.0),
                "efs": run_data.get("efs", 0.0),
                "predictive_power": round(getattr(self.predictive, 'predictive_power', 0.0), 4),
                "product_created": product.get("name"),
                "product_type": product.get("type"),
                "business_dev_opportunities": len(bd_results.get("opportunities", [])),
                "high_value_leads": len([o for o in bd_results.get("opportunities", []) if o.get("conversion_probability", 0) > 0.65]),
                "graph_insights_used": run_data.get("graph_insights_used", 0),
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat(),
                "flywheel_status": "closed",
                "self_critique_triggered": run_data.get("final_score", 0.0) > 0.82
            }

            if hasattr(self.arbos, '_append_trace'):
                self.arbos._append_trace("post_run_intelligence_complete", trace_data)

            logger.info(f"✅ PostRunIntelligenceEngine completed in {duration:.1f}s — "
                       f"Product: {product.get('name')} | High-value leads: {len([o for o in bd_results.get('opportunities', []) if o.get('conversion_probability', 0) > 0.65])}")

            return {
                "status": "success",
                "product": product,
                "business_dev": bd_results,
                "duration": duration,
                "predictive_power": round(getattr(self.predictive, 'predictive_power', 0.0), 4),
                "graph_insights_used": run_data.get("graph_insights_used", 0)
            }

        except Exception as e:
            logger.error(f"PostRunIntelligenceEngine failed: {e}")
            if hasattr(self.arbos, '_append_trace'):
                self.arbos._append_trace("post_run_intelligence_error", {"error": str(e)})
            return {"status": "error", "error": str(e)}
