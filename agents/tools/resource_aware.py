# agents/tools/resource_aware.py
# Real 4h H100 timing and auto-compression

import time
import psutil

class ResourceMonitor:
    def __init__(self, max_hours=3.8):
        self.max_seconds = max_hours * 3600
        self.start_time = time.time()
        print(f"⏱️  Resource monitor started (max {max_hours}h on H200)")

    def check_runtime(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_seconds:
            print("⏰ Runtime exceeded limit — forcing compression!")
            return "COMPRESSED"
        remaining = self.max_seconds - elapsed
        print(f"⏱️  Elapsed: {elapsed/3600:.2f}h | Remaining: {remaining/3600:.2f}h")
        return "OK"

    def compress_if_needed(self, output: str):
        if self.check_runtime() == "COMPRESSED":
            return output[:len(output)//2] + " [AUTO-COMPRESSED to fit H100]"
        return output
