# agents/tools/scienceclaw.py
# ScienceClaw × Infinite - multi-agent swarm coordination

def run_scienceclaw(task: str, swarm_size: int = 20):
    sc_path = "tools/scienceclaw"
    
    # Step 1: Clone the official repo ONLY the first time
    if not os.path.exists(sc_path):
        print("📥 Cloning ScienceClaw from GitHub...")
        subprocess.run(["git", "clone", "https://github.com/lamm-mit/scienceclaw.git", sc_path], check=True)
    
    # Step 2: Run the actual swarm script and pass your task + size
    print(f"🧪 Running ScienceClaw swarm ({swarm_size} agents) for: {task[:80]}...")
    result = subprocess.run(
        ["python", f"{sc_path}/run_swarm.py", "--task", task, "--size", str(swarm_size)],   # ← Real call
        capture_output=True,
        text=True,
        timeout=600
    )
    
    return f"✅ ScienceClaw Swarm Result:\n{result.stdout.strip()[:500]}..."
