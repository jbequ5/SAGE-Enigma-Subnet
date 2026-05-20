# em_ios/team_composer_client.py
"""
TeamComposer Client Wrapper for EM/iOS (Enigma Machine client)

This is the thin, clean interface that the local Enigma Machine (iOS / EM repo)
uses to request a team composition for any task/subtask.

It calls the canonical TeamComposer in the private Synapse intelligence layer.
No heavy logic here — just clean delegation with the exact same return format
the old placeholder used.
"""

import logging
from typing import Dict, Any

# Import the real intelligence-side TeamComposer (same Python environment or via package)
from synapse.team_composer import TeamComposer
from synapse.neural_operator_bank import NeuralOperatorBank
from synapse.mode import MODEMixture
from intelligence.fitness_landscape import NeurELAEmbedder

logger = logging.getLogger(__name__)


class TeamComposerClient:
    """
    Client-side wrapper for the EM/iOS repo.
    Provides the exact same public API as the old placeholder while delegating
    to the full, landscape-guided TeamComposer in the Synapse intelligence layer.
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

        # Initialize the full intelligence components once
        self.embedder = NeurELAEmbedder()
        self.bank = NeuralOperatorBank()
        self.mode = MODEMixture(self.embedder, self.bank)
        self.composer = TeamComposer(self.bank, self.mode, self.embedder)

        # Wire the fitness landscape
        self.bank.set_embedder(self.embedder)

        logger.info("✅ TeamComposerClient initialized — connected to live Synapse intelligence layer")

    def compose_team(self, task: str, challenge_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public API used by the Enigma Machine client.
        Returns exactly the same structure as the old placeholder.
        """
        result = self.composer.compose_team(task, challenge_context)

        logger.info(f"✅ Team composed for task '{task}' (ID: {result['team_composition_id']})")
        return result

    def verify_subtask_complete(self, results: Dict, checklist: List[Dict]) -> bool:
        """Delegate to the real verifier."""
        return self.composer.verify_subtask_complete(results, checklist)


# Global singleton instance for easy use in the EM/iOS client
team_composer = TeamComposerClient()


# Quick self-test
if __name__ == "__main__":
    client = TeamComposerClient()
    test_context = {
        "fragment": Fragment(
            fragment_id="test-123",
            timestamp=0.0,
            objectives_7d=torch.rand(7),
            physics_residuals=torch.rand(10),
            uncertainty_maps=torch.rand(10),
            efs_lift=0.85,
            verifier_checklist={"physics_ok": True},
            red_team_score=0.9,
            training_utility_score=0.88
        )
    }
    result = client.compose_team("turbulent_flow_test", test_context)
    print("✅ team_composer_client.py — full production client wrapper loaded and tested")
    print(f"   Team composition ID: {result['team_composition_id']}")
    print(f"   Shadow test passed: {result['shadow_test_passed']}")
