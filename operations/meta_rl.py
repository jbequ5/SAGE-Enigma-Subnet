# operations/meta_rl.py
import json
from pathlib import Path
from datetime import datetime
from .performance_tracker import PerformanceTracker

class MetaRL:
    """Meta-Reinforcement Learning nightly polisher for the Fragment Factory."""

    def __init__(self):
        self.weights_path = Path("data/meta_weights.json")
        self.weights_path.parent.mkdir(parents=True, exist_ok=True)
        self.weights = self._load_weights()

    def _load_weights(self) -> dict:
        if self.weights_path.exists():
            with open(self.weights_path) as f:
                return json.load(f)
        # Default meta-weights
        return {
            "global_yield_target": 0.85,
            "map_profile_bias": {"deterministic_heavy": 1.0, "balanced_hybrid": 1.25, "exploration_heavy": 1.1},
            "router_model_bonus": 0.15,
            "orchestrator_recovery_sensitivity": 0.8,
            "flight_test_branching_aggression": 1.0,
            "last_updated": datetime.now().isoformat()
        }

    def save_weights(self):
        with open(self.weights_path, "w") as f:
            json.dump(self.weights, f, indent=2)

    def run_nightly(self):
        """Run nightly Meta-RL update based on real Fragment Yield data."""
        tracker = PerformanceTracker()
        recent_runs = tracker.conn.execute("""
            SELECT profile_id, AVG(fragment_yield) as avg_yield, COUNT(*) as count
            FROM runs WHERE run_type = 'swarm_end' 
            GROUP BY profile_id ORDER BY avg_yield DESC
        """).fetchall()

        if not recent_runs:
            print("Meta-RL: No new data yet.")
            return

        # Simple policy update: boost high-yield profiles
        for row in recent_runs:
            profile_id = row[0]
            avg_yield = row[1]
            if avg_yield > self.weights["global_yield_target"]:
                if profile_id in self.weights["map_profile_bias"]:
                    self.weights["map_profile_bias"][profile_id] *= 1.08  # 8% boost

        self.weights["last_updated"] = datetime.now().isoformat()
        self.save_weights()
        print(f"✅ Meta-RL updated — new average Fragment Yield bias applied. Last run: {self.weights['last_updated']}")
