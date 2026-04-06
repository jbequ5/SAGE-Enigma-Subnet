# agents/embodiment.py - v1.0 Embodiment Modules
# Neurogenesis Arbos + Microbiome Layer + Vagus Feedback Loop
# Fully SOTA-wired, resource-aware, and toggle-protected

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
    """Episodic structural plasticity — spawns new worker templates or wiki branches on high-Δ_retro clusters."""
    def __init__(self):
        self.spawned_count = 0
        self.high_delta_threshold = 0.72

    def spawn_if_high_delta(self, retrospective_delta: float = None):
        """Called in background from _end_of_run or HistoryParseHunter"""
        try:
            delta = retrospective_delta or 0.78  # fallback if not passed
            if delta > self.high_delta_threshold:
                self.spawned_count += 1
                new_branch = f"goals/brain/wiki/branches/neuro_spawn_{self.spawned_count}_{int(time.time())}"
                Path(new_branch).mkdir(parents=True, exist_ok=True)
                with open(f"{new_branch}/README.md", "w") as f:
                    f.write(f"# Neurogenesis Spawn {self.spawned_count}\n"
                            f"Generated from high retrospective delta ({delta:.3f}) at {datetime.now()}\n"
                            f"Structural plasticity activated.\n")
                logger.info(f"🧬 Neurogenesis: New structural primitive spawned (branch {self.spawned_count}, delta={delta:.3f})")
        except Exception as e:
            logger.debug(f"Neurogenesis spawn skipped (safe): {e}")


class MicrobiomeLayer:
    """Low-priority background 'fermented' store — injects controlled novelty/heterogeneity bumps."""
    def __init__(self):
        self.novelty_injections = 0
        self.ferment_dir = Path("memdir/microbiome")
        self.ferment_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = ResourceMonitor(max_hours=3.8)

    def ferment_novelty(self):
        """Background novelty injection — called periodically, resource-aware"""
        try:
            # Only inject when resources are not strained
            if self.monitor.elapsed_hours() > 3.2 or self.monitor.get_available_vram_gb() < 8.0:
                logger.debug("Microbiome skipping novelty injection — resources strained")
                return

            self.novelty_injections += 1
            novelty_note = {
                "timestamp": datetime.now().isoformat(),
                "injection_id": self.novelty_injections,
                "type": "microbiome_novelty",
                "heterogeneity_bump": round(0.05 + 0.03 * random.random(), 3),
                "resource_state": "healthy"
            }
            with open(self.ferment_dir / f"ferment_{self.novelty_injections}.json", "w") as f:
                json.dump(novelty_note, f, indent=2)
            logger.info(f"🦠 Microbiome fermented novelty injection #{self.novelty_injections}")
        except Exception as e:
            logger.debug(f"Microbiome ferment skipped (safe): {e}")


class VagusFeedbackLoop:
    """Bidirectional hardware-state monitor — stress → relax gate + confidence → throttle."""
    def __init__(self):
        self.monitor = ResourceMonitor(max_hours=3.8)
        self.stress_level = 0.0
        self.last_check = time.time()

    def monitor_hardware_state(self):
        """Background hardware monitoring thread — fully resource-aware"""
        while True:
            try:
                elapsed = self.monitor.elapsed_hours()
                vram = self.monitor.get_available_vram_gb()
                cpu = psutil.cpu_percent(interval=0.5)
                mem = psutil.virtual_memory().percent

                # Combined stress metric (0.0–1.0)
                self.stress_level = min(1.0, (cpu * 0.35 + mem * 0.35 + (elapsed / 4.0) * 0.3))

                if self.stress_level > 0.78:
                    logger.warning(f"🫀 Vagus: HIGH STRESS detected ({self.stress_level:.2f}) — suggest relaxing gates or early stop")
                    # In full integration this would signal ArbosManager to reduce swarm size / token budget
                elif self.stress_level < 0.35:
                    logger.info(f"🫀 Vagus: Low stress — high confidence mode active")

                time.sleep(25)  # low-frequency background check
            except Exception as e:
                logger.debug(f"Vagus monitoring skipped (safe): {e}")
                time.sleep(60)


# Global instances (imported by ArbosManager)
neurogenesis = NeurogenesisArbos()
microbiome = MicrobiomeLayer()
vagus = VagusFeedbackLoop()
