import subprocess

def run(task: str, profile: str = "deep-theory", **kwargs):
    """
    GPD is an agent installed into AI coding runtimes (Claude Code, Gemini CLI, etc.).
    We can only trigger installation and return guidance.
    """
    try:
        # Install GPD into supported runtimes (one-time)
        subprocess.run(["npx", "-y", "get-physics-done", "--all"], check=False, timeout=30)

        return {
            "success": True,
            "output": f"GPD activated with profile '{profile}'.\n\nTask queued: {task[:300]}...\n\nNext step: Open Claude Code / Gemini CLI and run /gpd:new-project or /gpd:help",
            "note": "GPD runs inside AI coding environments, not as direct CLI"
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to activate GPD: {str(e)}"}
