import subprocess
from pathlib import Path

def run(task: str, intensity: str = "high", max_sources: int = 15, **kwargs):
    """
    Realistic ScienceClaw call using scienceclaw-post.
    """
    try:
        # Assume agent is already set up via setup.py
        cmd = ["scienceclaw-post", "--agent", "EnigmaAgent", "--topic", task, "--community", "mixed"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None
        }
    except FileNotFoundError:
        return {"success": False, "error": "scienceclaw-post command not found. Run setup.py first."}
    except Exception as e:
        return {"success": False, "error": str(e)}
