import subprocess

def run(task: str, search_mode: str = "deep", **kwargs):
    """Your personal AI-Researcher instance."""
    try:
        cmd = ["npx", "-y", "ai-researcher", "--mode", search_mode, "--task", task]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {"success": result.returncode == 0, "output": result.stdout.strip(), "error": result.stderr.strip() if result.stderr else None}
    except Exception as e:
        return {"success": False, "error": str(e)}
