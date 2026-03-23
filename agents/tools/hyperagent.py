# agents/tools/hyperagent.py
# Real integration with HyperAgents (facebookresearch) - self-referential self-improving agents

import subprocess
import os

def run_hyperagent(task: str):
    """
    Calls the real HyperAgents repo from facebookresearch.
    Clones once if needed, then runs the self-improving agent.
    """
    repo_path = "tools/hyperagents"
    
    if not os.path.exists(repo_path):
        print("📥 Cloning HyperAgents from GitHub (facebookresearch)...")
        subprocess.run([
            "git", "clone", "https://github.com/facebookresearch/HyperAgents.git", repo_path
        ], check=True)
    
    print(f"🔄 Running HyperAgent for: {task[:80]}...")
    try:
        result = subprocess.run([
            "python", f"{repo_path}/main.py", "--task", task
        ], capture_output=True, text=True, timeout=600)
        return f"✅ HyperAgent Result:\n{result.stdout.strip()[:600]}..."
    except Exception as e:
        return f"⚠️ HyperAgent failed: {str(e)}"
