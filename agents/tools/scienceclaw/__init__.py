import subprocess

def run(task: str, intensity: str = "high", max_sources: int = 15, **kwargs):
    """
    ScienceClaw uses the 'scienceclaw-post' CLI command.
    """
    try:
        cmd = [
            "scienceclaw-post",
            "--agent", "EnigmaMiner",
            "--topic", task,
            "--community", "mixed"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None
        }
    except FileNotFoundError:
        return {"success": False, "error": "scienceclaw-post command not found. Run the ScienceClaw installation script first."}
    except Exception as e:
        return {"success": False, "error": str(e)}
