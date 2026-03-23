# agents/tools/scienceclaw.py
# ScienceClaw × Infinite - multi-agent swarm coordination

import subprocess
import os

def run_scienceclaw(task: str, swarm_size: int = 20):
    path = "tools/scienceclaw"
    if not os.path.exists(path):
        print("📥 Cloning real ScienceClaw repo...")
        subprocess.run(["git", "clone", "https://github.com/lamm-mit/scienceclaw.git", path], check=True)
    print(f"🧪 Running real ScienceClaw swarm ({swarm_size} agents)...")
    try:
        result = subprocess.run(["python", f"{path}/run_swarm.py", "--task", task, "--size", str(swarm_size)], capture_output=True, text=True, timeout=600)
        return f"✅ ScienceClaw Result:\n{result.stdout.strip()[:500]}..."
    except Exception as e:
        return f"⚠️ ScienceClaw failed: {str(e)}"
