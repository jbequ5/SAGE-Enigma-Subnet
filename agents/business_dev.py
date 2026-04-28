import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class BusinessDev:
    """SOTA BusinessDev Wing — graph-driven hunt cycle, predictive scoring, PD Arm synthesis, and vault routing."""

    def __init__(self, arbos_manager=None):
        self.arbos = arbos_manager
        self.tool_hunter = getattr(arbos_manager, "tool_hunter", None)
        self.predictive = getattr(arbos_manager, "predictive", None)
        self.memory_layers = getattr(arbos_manager, "memory_layers", None)
        self.fragment_tracker = getattr(arbos_manager, "fragment_tracker", None)
        self.intelligence = getattr(arbos_manager, "intelligence", None)
        self.pd_arm = getattr(arbos_manager, "pd_arm", None)

        # Simple in-memory CRM for lead tracking
        self.crm = self._fallback_crm()

        # Wire back to ToolHunter for bidirectional flow
        if self.tool_hunter:
            self.tool_hunter.business_dev = self

        logger.info("📈 BusinessDev Wing v0.9.13+ SOTA — full graph intelligence + predictive flywheel enabled")

    def _fallback_crm(self):
        class FallbackCRM:
            def __init__(self):
                self.leads = []
            def track_lead(self, lead, proposal=None, predicted_conversion=0.0):
                self.leads.append({
                    "lead": lead,
                    "proposal": proposal,
                    "conversion_probability": predicted_conversion,
                    "timestamp": datetime.now().isoformat()
                })
        return FallbackCRM()

    def run_hunt_cycle(self, user_query: str = None) -> Dict[str, Any]:
        """Main intelligent hunt cycle — graph-driven + predictive scoring + PD Arm synthesis."""
        query = user_query or "market demand OR alpha opportunity OR vault synthesis OR high-value lead"

        logger.info(f"🔍 BusinessDev hunt cycle started — query: {query[:100]}...")

        # 1. Deep graph hunt (ByteRover MAU + freshness)
        graph_insights = []
        if self.fragment_tracker and hasattr(self.fragment_tracker, 'query_relevant_fragments'):
            graph_insights = self.fragment_tracker.query_relevant_fragments(
                query=query, top_k=15, min_score=0.68
            )

        # 2. ToolHunter + fused graph context
        fused_context = {}
        if self.tool_hunter:
            fused_context = self.tool_hunter.hunt_and_integrate(
                gap_description="Business development and lead generation opportunities using graph vault intelligence",
                subtask=query,
                challenge_context="Enigma Agentic Forge alpha demand sensing"
            )

        # 3. Discover raw opportunities
        raw_opportunities = self.tool_hunter.discover_lead_gen_tools(fused_context) if self.tool_hunter else []

        processed_opps = []
        high_value_count = 0

        for opp in raw_opportunities[:12]:
            # Predictive market demand scoring
            market_signals = {}
            if self.predictive and hasattr(self.predictive, 'sense_market_demand'):
                market_signals = self.predictive.sense_market_demand(opp)
            else:
                market_signals = {
                    "market_demand_score": 0.65,
                    "conversion_probability": 0.55,
                    "value_return": 0.0
                }

            lead_data = opp.get("lead", opp)
            proposal = opp.get("ideas", [{}])[0] if opp.get("ideas") else {}

            # CRM tracking
            if hasattr(self.crm, 'track_lead'):
                self.crm.track_lead(
                    lead=lead_data,
                    proposal=proposal,
                    predicted_conversion=market_signals.get("conversion_probability", 0.0)
                )

            # High-value lead → route to vaults + synthesize product
            if market_signals.get("conversion_probability", 0) > 0.65:
                high_value_count += 1
                run_data = {
                    "insight_score": market_signals.get("conversion_probability", 0),
                    "key_takeaway": f"High-potential lead from graph: {lead_data.get('domain', 'unknown')}",
                    "predictive_power": getattr(self.predictive, 'predictive_power', 0.0),
                    "flywheel_step": "bd_to_vaults_pd",
                    "graph_insights_used": len(graph_insights)
                }
                if self.intelligence and hasattr(self.intelligence, 'route_to_vaults'):
                    self.intelligence.route_to_vaults(run_data)

                if self.pd_arm and hasattr(self.pd_arm, 'synthesize_product'):
                    product = self.pd_arm.synthesize_product(
                        vault_data=graph_insights,
                        market_signals=market_signals
                    )

            processed_opps.append({
                "lead": lead_data,
                "market_demand_score": market_signals.get("market_demand_score", 0.0),
                "conversion_probability": market_signals.get("conversion_probability", 0.0),
                "value_return": market_signals.get("value_return", 0.0),
                "graph_insights_used": len(graph_insights)
            })

        # Final trace
        self._append_trace("business_dev_hunt_cycle", {
            "opportunities_found": len(raw_opportunities),
            "high_potential_leads": high_value_count,
            "graph_insights_used": len(graph_insights),
            "avg_predictive_power": round(getattr(self.predictive, 'predictive_power', 0.0), 4)
        })

        return {
            "status": "success",
            "opportunities": processed_opps,
            "graph_insights_used": len(graph_insights),
            "high_value_leads": high_value_count
        }

    def _append_trace(self, event_type: str, data: Dict):
        """Safe trace logging — delegates to ArbosManager if available."""
        if self.arbos and hasattr(self.arbos, '_append_trace'):
            self.arbos._append_trace(event_type, data)
        else:
            logger.info(f"[BusinessDev Trace] {event_type}: {data}")
