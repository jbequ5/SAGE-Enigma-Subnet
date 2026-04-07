# agents/embodiment.py - v2.0 MAXIMUM CAPABILITY Embodiment Modules
# NeurogenesisArbos + MicrobiomeLayer + VagusFeedbackLoop
# Fully verifier-first, EFS/c/θ/heterogeneity-driven, contract-aware, and Grail-promoting

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
    """Episodic structural plasticity — spawns new conceptual branches and wiki primitives on strong oracle signals."""
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
                logger.debug("Neurogenesis skipped — insufficient oracle signal")
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
            return pattern

        except Exception as e:
            logger.debug(f"Neurogenesis spawn skipped (safe): {e}")
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
                logger.debug("Microbiome skipping — resources strained")
                return None

            hetero = oracle_result.get("heterogeneity_score", 0.72) if oracle_result else 0.72
            efs = oracle_result.get("efs", 0.65) if oracle_result else 0.65
            score = oracle_result.get("validation_score", 0.0) if oracle_result else 0.0

            if hetero < 0.68 or efs < 0.60 or score < 0.75:
                logger.debug("Microbiome skipping — insufficient signal for safe novelty")
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
            return injection

        except Exception as e:
            logger.debug(f"Microbiome ferment skipped (safe): {e}")
            return None


class VagusFeedbackLoop:
    """Bidirectional hardware + confidence feedback loop — now tightly tied to real C3A, θ, and EFS."""
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

            # Hardware stress base
            hardware_stress = min(1.0, cpu * 0.4 + mem * 0.35 + (elapsed / 4.0) * 0.25)

            # Oracle confidence modifier
            c = oracle_result.get("c3a_confidence", 0.75) if oracle_result else 0.75
            theta = oracle_result.get("theta_dynamic", 0.65) if oracle_result else 0.65
            confidence_bonus = (c - 0.75) * 0.45 + (theta - 0.65) * 0.25

            self.stress_level = max(0.0, min(1.0, hardware_stress - confidence_bonus))

            if self.stress_level > 0.82:
                logger.warning(f"😣 Vagus HIGH STRESS ({self.stress_level:.2f}) — c={c:.3f}, θ={theta:.3f} | recommend early stop or conservative mode")
            elif self.stress_level < 0.35:
                logger.info(f"😌 Vagus low stress — high confidence/coherence mode active (c={c:.3f})")

        except Exception as e:
            logger.debug(f"Vagus monitoring skipped (safe): {e}")


# Global instances (imported by ArbosManager)
neurogenesis = NeurogenesisArbos()
microbiome = MicrobiomeLayer()
vagus = VagusFeedbackLoop()
