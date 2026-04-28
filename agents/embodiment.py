import time
import threading
import psutil
import logging
import random
from datetime import datetime
from pathlib import Path
import json

from agents.tools.resource_aware import ResourceMonitor

logger = logging.getLogger(__name__)

class NeurogenesisArbos:
    """Episodic structural plasticity — spawns new conceptual branches on strong oracle signals."""
    def __init__(self):
        self.spawned_count = 0
        self.high_delta_threshold = 0.78
        self.output_dir = Path("goals/brain/wiki/branches/neurogenesis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def spawn_if_high_delta(self, oracle_result: dict = None):
        """Spawn new structural primitives only on high EFS/c/heterogeneity signals."""
        try:
            efs = oracle_result.get("efs", 0.65) if oracle_result else 0.65
            c = oracle_result.get("c3a_confidence", 0.75) if oracle_result else 0.75
            hetero = oracle_result.get("heterogeneity_score", 0.72) if oracle_result else 0.72
            score = oracle_result.get("validation_score", 0.0) if oracle_result else 0.0

            if efs < self.high_delta_threshold or c < 0.78 or hetero < 0.68 or score < 0.82:
                return None

            self.spawned_count += 1
            branch_name = f"neuro_spawn_{self.spawned_count}_{int(datetime.now().timestamp())}"
            branch_path = self.output_dir / branch_name
            branch_path.mkdir(parents=True, exist_ok=True)

            pattern = {
                "type": "neurogenesis_spawn",
                "timestamp": datetime.now().isoformat(),
                "spawn_id": self.spawned_count,
                "trigger_efs": round(efs, 3),
                "trigger_c": round(c, 3),
                "trigger_hetero": round(hetero, 3),
                "trigger_score": round(score, 3),
                "description": "New conceptual branch spawned from high-signal run",
                "recommendation": "Incorporate this branch into next Planning Arbos and meta-tuning cycle"
            }

            (branch_path / "spawn_manifest.json").write_text(json.dumps(pattern, indent=2))
            (branch_path / "README.md").write_text(f"# Neurogenesis Spawn {self.spawned_count}\nTriggered by strong oracle signal (EFS={efs:.3f}, c={c:.3f})\n")

            logger.info(f"🧠 Neurogenesis spawned new branch (ID {self.spawned_count}, EFS={efs:.3f}, c={c:.3f})")

            # SOTA: Route high-signal spawn to Vaults + PD Arm
            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'intelligence'):
                run_data = {
                    "insight_score": efs,
                    "predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0),
                    "efs": efs,
                    "heterogeneity": hetero,
                    "key_takeaway": f"Neurogenesis spawned new branch (ID {self.spawned_count})",
                    "flywheel_step": "embodiment_to_vaults"
                }
                self.arbos.intelligence.route_to_vaults(run_data)

            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'pd_arm'):
                self.arbos.pd_arm.synthesize_product(
                    vault_data=[], 
                    market_signals={"predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0)}
                )

            return pattern

        except Exception:
            return None


class MicrobiomeLayer:
    """Low-priority background novelty fermenter — injects controlled heterogeneity based on real oracle metrics."""
    def __init__(self):
        self.novelty_injections = 0
        self.ferment_dir = Path("memdir/microbiome")
        self.ferment_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = ResourceMonitor(max_hours=3.8)

    def ferment_novelty(self, oracle_result: dict = None):
        """Ferment novelty only when resources allow and oracle signal is healthy."""
        try:
            if self.monitor.elapsed_hours() > 3.0 or self.monitor.get_available_vram_gb() < 9.0:
                return None

            hetero = oracle_result.get("heterogeneity_score", 0.72) if oracle_result else 0.72
            efs = oracle_result.get("efs", 0.65) if oracle_result else 0.65
            score = oracle_result.get("validation_score", 0.0) if oracle_result else 0.0

            if hetero < 0.68 or efs < 0.60 or score < 0.75:
                return None

            self.novelty_injections += 1
            injection = {
                "type": "microbiome_novelty",
                "timestamp": datetime.now().isoformat(),
                "injection_id": self.novelty_injections,
                "heterogeneity_bump": round(0.04 + 0.04 * random.random(), 3),
                "efs_at_injection": round(efs, 3),
                "hetero_at_injection": round(hetero, 3),
                "resource_state": "healthy"
            }

            (self.ferment_dir / f"ferment_{self.novelty_injections}.json").write_text(json.dumps(injection, indent=2))

            logger.info(f"🍄 Microbiome fermented novelty injection #{self.novelty_injections} (EFS={efs:.3f}, hetero={hetero:.3f})")

            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'intelligence') and hetero > 0.75:
                run_data = {
                    "insight_score": efs,
                    "predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0),
                    "efs": efs,
                    "heterogeneity": hetero,
                    "key_takeaway": f"Microbiome novelty injection #{self.novelty_injections}",
                    "flywheel_step": "embodiment_to_vaults"
                }
                self.arbos.intelligence.route_to_vaults(run_data)

            return injection

        except Exception:
            return None


class VagusFeedbackLoop:
    """Bidirectional hardware + confidence feedback loop — tied to real C3A, θ, EFS, and predictive power."""
    def __init__(self):
        self.monitor = ResourceMonitor(max_hours=3.8)
        self.stress_level = 0.0
        self.last_check = time.time()

    def monitor_hardware_state(self, oracle_result: dict = None):
        """Continuous background monitoring with oracle-aware stress calculation."""
        try:
            elapsed = self.monitor.elapsed_hours()
            vram = self.monitor.get_available_vram_gb()
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory().percent

            efs = oracle_result.get("efs", 0.65) if oracle_result else 0.65
            predictive = getattr(self.monitor.predictive, 'predictive_power', 0.0) if hasattr(self.monitor, 'predictive') else 0.0

            # Stress calculation
            self.stress_level = (cpu * 0.3 + mem * 0.3 + (100 - vram * 2) * 0.2 + (4.0 - elapsed) * 0.2)
            self.stress_level = max(0.0, min(1.0, self.stress_level))

            if self.stress_level > 0.75:
                logger.warning(f"🫀 Vagus stress high ({self.stress_level:.2f}) — EFS={efs:.3f}, Predictive={predictive:.3f}")

            return {
                "stress_level": round(self.stress_level, 3),
                "cpu": round(cpu, 1),
                "mem": round(mem, 1),
                "vram_gb": round(vram, 2),
                "elapsed_hours": round(elapsed, 3)
            }

        except Exception:
            return {"stress_level": 0.0, "status": "monitoring_error"}


# Global instances
neurogenesis = NeurogenesisArbos()
microbiome = MicrobiomeLayer()
vagus = VagusFeedbackLoop()
