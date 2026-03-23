# agents/tools/gpd.py
# Get Physics Done - derivations & verification

def run_gpd(task: str):
    gpd_path = "tools/gpd"
    
    # Step 1: Clone the official repo ONLY the first time
    if not os.path.exists(gpd_path):
        print("📥 Cloning GPD from GitHub...")
        subprocess.run(["git", "clone", "https://github.com/psi-oss/get-physics-done.git", gpd_path], check=True)
    
    # Step 2: Run the actual GPD script and pass your task
    print(f"📐 Running GPD for: {task[:80]}...")
    result = subprocess.run(
        ["python", f"{gpd_path}/gpd.py", task],   # ← This runs the real GPD
        capture_output=True,
        text=True,
        timeout=300
    )
    
    return f"✅ GPD Result:\n{result.stdout.strip()[:500]}..."
