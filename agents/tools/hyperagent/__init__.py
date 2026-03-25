import subprocess

def run(task: str, parallel_tasks: int = 5, **kwargs):
    """
    HyperAgent - uses generate_loop.py from the repo.
    """
    try:
        cmd = ["python", "agents/tools/hyperagent/HyperAgents/generate_loop.py", "--task", task]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
