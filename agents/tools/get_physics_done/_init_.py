# agents/tools/get_physics_done/__init__.py
"""
Wrapper for the real Get Physics Done (psi-oss) agentic AI physicist.
"""

import subprocess
from pathlib import Path

def run_gpd(task: str, profile: str = "deep-theory", tier: str = "1", **kwargs):
    """
    Run Get Physics Done with your chosen configuration.
    This is your personal instance.
    """
    try:
        # For now we call it via npx (you can change to local install later)
        cmd = [
            "npx", "-y", "get-physics-done",
            "--profile", profile,
            "--tier", tier,
            task
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "profile_used": profile,
            "tier_used": tier
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
