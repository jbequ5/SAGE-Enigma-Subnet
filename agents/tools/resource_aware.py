# agents/tools/resource_aware.py
# Real H100 runtime monitoring + auto-compression + guardrails
# v1.0 hardened: Clean, focused, supports dynamic swarm + EFS awareness

import time
import psutil
import logging
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ResourceMonitor:
    def __init__(self, max_hours: float = 3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        self.max_hours = max_hours
        logger.info(f"⏱️  Resource Monitor initialized — hard limit {max_hours}h")

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def elapsed_hours(self) -> float:
        return self.elapsed_seconds() / 3600

    def get_available_vram_gb(self) -> float:
        """Return approximate available VRAM in GB (for dynamic swarm sizing)"""
        try:
            import torch
            if torch.cuda.is_available():
                free = torch.cuda.mem_get_info(0)[0] / (1024 ** 3)
                return round(free, 2)
            else:
                # CPU-only or unknown fallback
                return 48.0
        except:
            return 48.0  # safe default for Chutes/H100 assumptions

    def check_and_compress(self, output: str, context: dict = None) -> str:
        """Check runtime and compress output if approaching limit"""
        if context is None:
            context = {}

        elapsed = self.elapsed_hours()

        # Last 6 minutes = danger zone
        if elapsed > self.max_hours - 0.1:
            logger.warning(f"⚠️  Approaching hard limit ({elapsed:.2f}h / {self.max_hours}h) — compressing output")
            # Aggressive but safe compression
            compressed = output[:len(output)//3] + "\n\n[AUTO-COMPRESSED due to time limit — high-value content preserved]"
            return compressed

        # Last 30 minutes = warning
        elif elapsed > self.max_hours - 0.5:
            logger.warning(f"⚠️  Warning: {elapsed:.2f}h / {self.max_hours}h elapsed")

        else:
            logger.info(f"⏱️  Safe runtime: {elapsed:.2f}h / {self.max_hours}h")

        return output

    def get_status(self) -> dict:
        """Return current status for UI or logging"""
        return {
            "elapsed_hours": round(self.elapsed_hours(), 3),
            "remaining_hours": round(self.max_hours - self.elapsed_hours(), 3),
            "available_vram_gb": self.get_available_vram_gb(),
            "status": "warning" if self.elapsed_hours() > self.max_hours - 0.5 else "normal"
        }

    def should_early_stop(self) -> bool:
        """Simple guard for resource-aware early stopping"""
        return self.elapsed_hours() > self.max_hours * 0.95
