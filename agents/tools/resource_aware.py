# agents/tools/resource_aware.py
# Real runtime monitoring + auto-compression for 4h H100 limit

import time
import psutil

class ResourceMonitor:
    def __init__(self, max_hours: float = 3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        print(f"⏱️  H100 Resource Monitor started — max {max_hours} hours on H100")

    def elapsed_hours(self) -> float:
        return (time.time() - self.start_time) / 3600

    def check_and_compress(self, output: str) -> str:
        elapsed = self.elapsed_hours()
        if elapsed > 3.8:
            print(f"⏰ Exceeded H100 limit ({elapsed:.2f}h) — compressing output")
            return output[:len(output)//2] + " [AUTO-COMPRESSED to fit H100]"
        print(f"⏱️  Current runtime: {elapsed:.2f}h / 3.8h on H100")
        return output
