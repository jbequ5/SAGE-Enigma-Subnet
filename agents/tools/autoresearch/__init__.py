"""
Full integration of karpathy/autoresearch into Enigma Machine Miner.
Uses and updates program.md cumulatively so tools build on each other.
"""

import subprocess
from pathlib import Path

def run(task: str, depth: str = "medium", iterations: int = 3, program_md_path: str = "program.md", **kwargs):
    """
    Run AutoResearch with full program.md support.
    
    - Reads existing program.md (cumulative context)
    - Appends the new task
    - Runs AutoResearch
    - Returns the updated program.md for the next tool in the chain
    """
    program_path = Path(program_md_path)
    
    # Initialize or append to program.md
    if not program_path.exists():
        initial = f"# AutoResearch Execution Program\n\n## Original Challenge\n{task}\n\n"
        program_path.write_text(initial)
    else:
        current = program_path.read_text()
        program_path.write_text(current + f"\n\n## New Task from Miner\n{task}\n\n")

    try:
        cmd = [
            "npx", "-y", "autoresearch",
            "--depth", depth,
            "--iterations", str(iterations),
            "--task", task,
            "--program", str(program_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        # Read the final updated program.md
        final_program = program_path.read_text() if program_path.exists() else ""

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip() if result.stderr else None,
            "program_md": final_program,           # Pass this to next tool
            "depth_used": depth,
            "iterations_used": iterations
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "AutoResearch timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}
