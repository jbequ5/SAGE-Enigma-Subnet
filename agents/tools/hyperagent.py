# agents/tools/hyperagent.py
# Real integration with HyperAgents (facebookresearch) - self-referential self-improving agents

import subprocess
import os

def run_hyperagent(task: str):
    path = "tools/hyperagents"
    if not os.path.exists(path):
        print("📥 Cloning real HyperAgents repo...")
        subprocess.run(["git", "clone", "https://github.com/facebookresearch/HyperAgents.git", path], check=True)
    print(f"🔄 Running real HyperAgent for: {task[:80]}...")
    try:
        result = subprocess.run(["python", f"{path}/main.py", "--task", task], capture_output=True, text=True, timeout=600)
        return f"✅ HyperAgent Result:\n{result.stdout.strip()[:600]}..."
    except Exception as e:
        return f"⚠️ HyperAgent failed: {str(e)}"
