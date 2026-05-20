# em_ios/fragment_scoring_client.py
"""
Fragment Scoring Client Wrapper for EM/iOS (Enigma Machine client)

Thin, clean interface that the local Enigma Machine uses to compute the 7-objective vector.
It delegates to the canonical scoring engine in the private Synapse intelligence layer.
"""

import logging
from typing import Dict, Any

# Import the real intelligence-side scoring engine
from synapse.fragment_scoring import FragmentScoringEngine, fragment_scoring_engine

logger = logging.getLogger(__name__)


class FragmentScoringClient:
    """
    Client-side wrapper for the EM/iOS repo.
    Provides the exact same public API the old placeholder would have used.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ FragmentScoringClient initialized — connected to Synapse intelligence layer")

    def compute_7_objective_vector(self, raw_fragment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Public API used by the Enigma Machine client."""
        result = fragment_scoring_engine.compute_7_objective_vector(raw_fragment_data)
        return {
            "objectives_7d": result.tolist() if hasattr(result, "tolist") else result,
            "timestamp": raw_fragment_data.get("timestamp", 0.0),
            "fragment_id": raw_fragment_data.get("fragment_id", "unknown")
        }

    def create_scored_fragment(self, raw_fragment_data: Dict[str, Any]):
        """Full pipeline: returns a complete scored Fragment object."""
        return fragment_scoring_engine.create_scored_fragment(raw_fragment_data)


# Global singleton instance for easy use in the EM/iOS client
fragment_scoring_client = FragmentScoringClient()


# Quick self-test
if __name__ == "__main__":
    test_data = {
        "fragment_id": "test-001",
        "timestamp": 0.0,
        "physics_residuals": [0.001, 0.0005],
        "uncertainty_maps": [0.05, 0.03],
        "efs_lift": 0.92,
        "verifier_checklist": {"physics_ok": True, "conservation_ok": True},
        "red_team_score": 0.95,
        "training_utility_score": 0.88,
        "domain_tag": "turbulent"
    }
    client = FragmentScoringClient()
    scored = client.create_scored_fragment(test_data)
    print("✅ em_ios/fragment_scoring_client.py — full production client wrapper loaded and tested")
    print(f"   7-objective vector computed successfully")
    print(f"   objectives_7d: {[round(v, 4) for v in scored.objectives_7d.tolist()]}")
