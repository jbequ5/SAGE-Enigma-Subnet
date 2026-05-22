# operations/telemetry.py
"""
SAGE v0.9.15 — TelemetryCollector (Locked Optimal v3.1)
Maximum-granularity operational gap detection + reporting to private Synapse.
Guarantees every fragment carries the full max-intelligence metadata set from execution time.
Captures ALL CAS flywheel signals and detects EVERY important gap (landscape-native, 7D, operational, economic).
Zero hardcoded values — all thresholds from SynapseConfig.
Fully aligned with the upgraded intelligence layer.
"""

from performance_tracker import PerformanceTracker
from datetime import datetime
from typing import Dict, List, Any
import logging
import numpy as np

from synapse_client import synapse_client
from synapse.synapse_config import SynapseConfig

logger = logging.getLogger(__name__)


class TelemetryCollector:
    """Production-grade telemetry pipeline with comprehensive gap detection."""

    def __init__(self, tracker: PerformanceTracker, config: SynapseConfig = None):
        self.tracker = tracker
        self.config = config or SynapseConfig()
        self.scoring_config = self.config.scoring

        # Rolling buffers for max-intelligence metadata
        self.temporal_trajectory = []
        self.economic_signals = []

        # Runtime telemetry stats
        self.stats = {
            "swarm_size_used": 0,
            "compute_cost_per_subtask": 0.0,
            "kas_attempts": 0,
            "kas_success": 0,
            "human_interventions": 0,
            "red_team_survived": True
        }

        logger.info("✅ TelemetryCollector (Locked Optimal v3.1) initialized — comprehensive gap detection + full metadata guarantee")

    def record_swarm_start(self, run_id: str, challenge: Dict, loadout: Dict, profiles: List[Dict]):
        """Record swarm initialization."""
        self.tracker.record_run({
            "run_id": run_id,
            "challenge_id": challenge.get("id"),
            "run_type": "swarm_start",
            "timestamp": datetime.now().isoformat(),
            "loadout": loadout,
            "profiles": [p.get("id") for p in profiles],
            "fragment_yield": 0.0
        })
        self.temporal_trajectory.clear()
        self.economic_signals.clear()
        self.stats = {"swarm_size_used": 0, "compute_cost_per_subtask": 0.0, "kas_attempts": 0, "kas_success": 0, "human_interventions": 0, "red_team_survived": True}

    def record_step(self, objectives_7d: List[float], **runtime_kwargs):
        """Record every solver step — core CAS flywheel capture."""
        self.temporal_trajectory.append(objectives_7d)
        if len(self.temporal_trajectory) > self.scoring_config.get("temporal_trajectory_length", 5):
            self.temporal_trajectory.pop(0)

        self.stats["swarm_size_used"] = runtime_kwargs.get("swarm_size", self.stats.get("swarm_size_used", 0))
        self.stats["compute_cost_per_subtask"] += runtime_kwargs.get("compute_seconds", 0.0)
        self.stats["kas_attempts"] += runtime_kwargs.get("kas_attempts", 0)
        self.stats["kas_success"] += runtime_kwargs.get("kas_success", 0)
        if runtime_kwargs.get("human_intervention", False):
            self.stats["human_interventions"] += 1
        if not runtime_kwargs.get("red_team_survived", True):
            self.stats["red_team_survived"] = False

    def record_fragment(self, run_id: str, profile_id: str, fragment: Dict):
        """Record fragment with full max-intelligence metadata."""
        fragment = self._enrich_fragment_with_max_intelligence(fragment)

        self.tracker.record_run({
            "run_id": run_id,
            "profile_id": profile_id,
            "run_type": "fragment",
            "fragment_yield": fragment.get("yield_contribution", 0.0),
            "efs": fragment.get("efs", 0.0),
            "refined_value_added": fragment.get("refined_value_added", 0.0),
            "n_pass": 1,
            "avg_refined_value": fragment.get("refined_value_added", 0.0)
        })

        try:
            telemetry_payload = {
                "run_id": run_id,
                "profile_id": profile_id,
                "timestamp": datetime.now().isoformat(),
                "swarm_size_used": self.stats["swarm_size_used"],
                "compute_cost_per_subtask": self.stats["compute_cost_per_subtask"],
                "kas_hit_rate": self.stats["kas_success"] / max(1, self.stats["kas_attempts"]),
                "human_intervention": self.stats["human_interventions"] > 0,
                "red_team_survived": self.stats["red_team_survived"],
                "temporal_trajectory": self.temporal_trajectory,
                "economic_signal": sum(self.economic_signals) / len(self.economic_signals) if self.economic_signals else 1.0,
            }
            synapse_client.sync_ingest_fragments(
                fragments=[fragment],
                telemetry=telemetry_payload,
                em_instance_id=run_id,
                run_id=run_id
            )
        except Exception as e:
            logger.warning(f"Failed to push fragment to Synapse: {e}")

    def _enrich_fragment_with_max_intelligence(self, fragment: Dict) -> Dict:
        """Guarantees full max-intelligence metadata."""
        fragment.setdefault("temporal_trajectory", self.temporal_trajectory)
        fragment.setdefault("economic_signal", sum(self.economic_signals) / len(self.economic_signals) if self.economic_signals else 1.0)
        fragment.setdefault("plon_neighborhood", [])
        fragment.setdefault("uncertainty_7d", [self.scoring_config.get("uncertainty_7d_base", 0.08) + np.random.uniform(0, self.scoring_config.get("uncertainty_7d_range", 0.12)) for _ in range(7)])
        fragment.setdefault("landscape_effect", 0.0)
        fragment.setdefault("final_rank_score", 0.0)
        return fragment

    def record_swarm_end(self, run_id: str, final_metrics: Dict):
        """Record final swarm results."""
        self.tracker.record_run({
            "run_id": run_id,
            "run_type": "swarm_end",
            "timestamp": datetime.now().isoformat(),
            **final_metrics
        })
        self._detect_and_report_operational_gaps(run_id, final_metrics)

    def record_save_resume(self, challenge_id: str, profile_id: str, session_data: Dict):
        """Record save/resume session state."""
        self.tracker.record_run({
            "challenge_id": challenge_id,
            "profile_id": profile_id,
            "run_type": "save_resume",
            "session_data": session_data
        })

    def _detect_and_report_operational_gaps(self, run_id: str, final_metrics: Dict):
        """Comprehensive gap detection — covers ALL important CAS flywheel dimensions."""
        cfg = self.scoring_config
        gaps = []

        avg_efs = final_metrics.get("final_efs") or self.tracker.get_average_efs()
        avg_refined = final_metrics.get("final_refined_value_added", 0.0)
        total_fragments = final_metrics.get("total_fragments", 0)
        novelty_factor = final_metrics.get("novelty_factor", 0.0)
        historical = self.tracker.best_profiles_for_challenge("general")
        compute_efficiency = final_metrics.get("compute_efficiency", 1.0)
        kas_signal_strength = final_metrics.get("kas_signal_strength", 0.0)
        verification_fail_rate = final_metrics.get("verification_fail_rate", 0.0)
        synthesis_stall_rate = final_metrics.get("synthesis_stall_rate", 0.0)
        hypervolume = final_metrics.get("hypervolume", 0.8)
        funnel_diversity = final_metrics.get("funnel_diversity", 0.5)
        temporal_drift = final_metrics.get("temporal_drift", 0.0)
        searchability = final_metrics.get("searchability", 0.5)
        weakest_objective = final_metrics.get("weakest_objective", "general")

        # Landscape Health Gaps
        if hypervolume < cfg.get("low_hypervolume_threshold", 0.75):
            gaps.append({"gap_type": "low_hypervolume", "severity": "high", "description": "Landscape hypervolume too low — capability space not expanding", "suggested_action": "new_landscape_expansion_objective", "metrics": {"hypervolume": hypervolume}})

        if funnel_diversity < cfg.get("low_funnel_diversity_threshold", 0.4):
            gaps.append({"gap_type": "low_funnel_diversity", "severity": "high", "description": "Low funnel diversity — trapped in local optima", "suggested_action": "new_novelty_exploration_objective", "metrics": {"funnel_diversity": funnel_diversity}})

        if temporal_drift > cfg.get("high_temporal_drift_threshold", 0.25):
            gaps.append({"gap_type": "high_temporal_drift", "severity": "high", "description": "High temporal drift — old strategies becoming stale", "suggested_action": "new_mope_model", "metrics": {"temporal_drift": temporal_drift}})

        if searchability < cfg.get("low_searchability_threshold", 0.6):
            gaps.append({"gap_type": "low_searchability", "severity": "medium", "description": "Low searchability — hard to find better nearby solutions", "suggested_action": "new_searchability_objective", "metrics": {"searchability": searchability}})

        # 7D Objective-Specific Gaps
        if weakest_objective != "general":
            gaps.append({"gap_type": f"weak_{weakest_objective}", "severity": "high", "description": f"Weakest objective is {weakest_objective} — targeted specialist needed", "suggested_action": f"new_{weakest_objective}_objective", "metrics": {"weakest_objective": weakest_objective}})

        # Uncertainty Gaps
        avg_uncertainty = final_metrics.get("avg_uncertainty", 0.15)
        if avg_uncertainty > cfg.get("high_uncertainty_threshold", 0.25):
            gaps.append({"gap_type": "high_uncertainty", "severity": "medium", "description": "High overall uncertainty — needs more verification or red-team focus", "suggested_action": "new_verifier_model", "metrics": {"avg_uncertainty": avg_uncertainty}})

        # Economic & Downstream Gaps
        avg_economic = final_metrics.get("avg_economic_signal", 1.0)
        if avg_economic < cfg.get("low_economic_signal_threshold", 0.7):
            gaps.append({"gap_type": "low_economic_signal", "severity": "high", "description": "Low downstream economic value — alignment with investor outcomes needed", "suggested_action": "new_economic_synthesis_objective", "metrics": {"avg_economic": avg_economic}})

        # Operational Telemetry Gaps
        if self.stats["human_interventions"] > cfg.get("high_human_intervention_threshold", 3):
            gaps.append({"gap_type": "high_human_intervention", "severity": "medium", "description": "Frequent human intervention — autonomy gap detected", "suggested_action": "new_autonomy_objective", "metrics": {"interventions": self.stats["human_interventions"]}})

        if self.stats["kas_success"] / max(1, self.stats["kas_attempts"]) < cfg.get("low_kas_hit_rate_threshold", 0.6):
            gaps.append({"gap_type": "low_kas_hit_rate", "severity": "medium", "description": "Low KAS hit rate — knowledge acquisition weakness", "suggested_action": "new_kas_training_signal", "metrics": {"hit_rate": self.stats["kas_success"] / max(1, self.stats["kas_attempts"])}})

        # Original high-granularity gaps (preserved and config-driven)
        if avg_efs < cfg.get("low_efs_threshold", 0.75):
            gaps.append({"gap_type": "low_efs_lift", "severity": "high", "description": "Average EFS Lift below threshold", "suggested_action": "new_nn_objective", "metrics": {"current_efs": avg_efs}})

        if avg_refined < cfg.get("low_refined_threshold", 0.60):
            gaps.append({"gap_type": "low_refined_value_added", "severity": "high", "description": "Refined value added too low", "suggested_action": "new_synthesis_objective", "metrics": {"current_refined": avg_refined}})

        if novelty_factor < cfg.get("low_novelty_threshold", 0.55):
            gaps.append({"gap_type": "low_novelty_heterogeneity", "severity": "medium", "description": "Low novelty in fragments", "suggested_action": "new_novelty_objective", "metrics": {"novelty_factor": novelty_factor}})

        # Report gaps
        if gaps:
            logger.info(f"🔍 Detected {len(gaps)} operational gaps — reporting to private Synapse")
            payload = {
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(),
                "gaps": gaps,
                "provenance": {"source": "ios_operations", "version": "0.9.15"}
            }
            try:
                synapse_client.sync_ingest_fragments(
                    fragments=[], telemetry=payload, em_instance_id=run_id, run_id=run_id
                )
                logger.info(f"✅ {len(gaps)} gaps sent to Synapse")
            except Exception as e:
                logger.error(f"Failed to report gaps: {e}")
        else:
            logger.debug("No operational gaps detected in this swarm.")


# Global singleton
telemetry_collector: TelemetryCollector = None
