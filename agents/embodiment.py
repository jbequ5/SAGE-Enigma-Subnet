# agents/embodiment.py - v0.6 Embodiment Modules
# Neurogenesis Arbos + Microbiome Layer + Vagus Feedback Loop
import time
import threading
import psutil
import logging
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class NeurogenesisArbos:
    """Episodic structural plasticity — spawns new worker templates or wiki branches when high-Δ_retro clusters form."""
    def __init__(self):
        self.spawned_count = 0
        self.high_delta_threshold = 0.72

    def spawn_if_high_delta(self):
        """Called in background from _end_of_run"""
        try:
            # In real use this would check recent retrospective scores
            recent_delta = 0.78  # placeholder — wired from HistoryParseHunter in full integration
            if recent_delta > self.high_delta_threshold:
                self.spawned_count += 1
                # Create new wiki branch or worker template
                new_branch = f"goals/brain/wiki/branches/neuro_spawn_{self.spawned_count}_{int(time.time())}"
                Path(new_branch).mkdir(parents=True, exist_ok=True)
                with open(f"{new_branch}/README.md", "w") as f:
                    f.write(f"# Neurogenesis Spawn {self.spawned_count}\nGenerated from high retrospective delta at {datetime.now()}\n")
                logger.info(f"🧬 Neurogenesis: New structural primitive spawned (branch {self.spawned_count})")
        except Exception as e:
            logger.debug(f"Neurogenesis spawn skipped (safe): {e}")


class MicrobiomeLayer:
    """Low-priority background 'fermented' store — injects controlled novelty/heterogeneity bumps."""
    def __init__(self):
        self.novelty_injections = 0
        self.ferment_dir = Path("memdir/microbiome")
        self.ferment_dir.mkdir(parents=True, exist_ok=True)

    def ferment_novelty(self):
        """Background novelty injection — called periodically"""
        try:
            self.novelty_injections += 1
            novelty_note = {
                "timestamp": datetime.now().isoformat(),
                "injection_id": self.novelty_injections,
                "type": "microbiome_novelty",
                "heterogeneity_bump": round(0.05 + 0.03 * random.random(), 3)
            }
            with open(self.ferment_dir / f"ferment_{self.novelty_injections}.json", "w") as f:
                json.dump(novelty_note, f, indent=2)
            logger.info(f"🦠 Microbiome fermented novelty injection #{self.novelty_injections}")
        except Exception as e:
            logger.debug(f"Microbiome ferment skipped (safe): {e}")


class VagusFeedbackLoop:
    """Bidirectional hardware-state monitor — stress → relax gate + confidence → throttle."""
    def __init__(self):2. 
        self.stress_level = 0.0
        self.last_check = time.time()

    def monitor_hardware_state(self):
        """Background hardware monitoring thread"""
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                self.stress_level = (cpu + mem) / 200.0  # normalized 0-1

                if self.stress_level > 0.75:
                    logger.warning(f"🫀 Vagus: High stress detected ({self.stress_level:.2f}) — relaxing gates")
                    # In full integration this would signal ArbosManager to reduce swarm size or token budget
                elif self.stress_level < 0.35:
                    logger.info(f"🫀 Vagus: Low stress — high confidence mode active")

                time.sleep(30)  # low-frequency background check
            except Exception as e:
                logger.debug(f"Vagus monitoring skipped (safe): {e}")
                time.sleep(60)


# Global instances (imported by ArbosManager)
neurogenesis = NeurogenesisArbos()
microbiome = MicrobiomeLayer()
vagus = VagusFeedbackLoop()
