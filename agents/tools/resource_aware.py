# agents/tools/resource_aware.py
# Real H100 runtime monitoring + auto-compression + guardrails

import time
import psutil
from pathlib import Path

class ResourceMonitor:
    def __init__(self, max_hours: float = 3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        self.max_hours = max_hours
        print(f"⏱️  H100 Resource Monitor initialized — hard limit {max_hours}h")

    def elapsed_seconds(self) -> float:
        return time.time() - self.start_time

    def elapsed_hours(self) -> float:
        return self.elapsed_seconds() / 3600

    def check_and_compress(self, output: str) -> str:
        """Check runtime and compress output if approaching limit"""
        elapsed = self.elapsed_hours()

        if elapsed > self.max_hours - 0.1:   # last 6 minutes = danger zone
            print(f"⚠️  Approaching H100 limit ({elapsed:.2f}h / {self.max_hours}h) — compressing output")
            # Aggressive compression
            compressed = output[:len(output)//3] + "\n\n[AUTO-COMPRESSED due to H100 time limit]"
            return compressed

        elif elapsed > self.max_hours - 0.5:   # last 30 minutes = warning
            print(f"⚠️  Warning: {elapsed:.2f}h / {self.max_hours}h elapsed on H100")

        else:
            print(f"⏱️  Safe runtime: {elapsed:.2f}h / {self.max_hours}h on H100")

        return output

    def get_status(self) -> dict:
        """Return current status for UI or logging"""
        return {
            "elapsed_hours": round(self.elapsed_hours(), 3),
            "remaining
