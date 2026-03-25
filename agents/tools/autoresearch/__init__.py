from pathlib import Path

def run(task: str, **kwargs):
    """
    Karpathy AutoResearch is NOT a CLI.
    It works by writing a program.md file that an AI coding agent (Claude/Cursor/etc.) then executes.
    """
    program_path = Path("program.md")
    content = f"""# AutoResearch Program for Enigma Miner

Task: {task}

Instructions for the AI coding agent:
- Read this file and start autonomous ML/research experiments
- Focus on novelty and high verifier score
- Keep experiments feasible under H100 time limits
- Iterate and improve only the best variants

Start the research loop now.
"""
    program_path.write_text(content)

    return {
        "success": True,
        "output": f"✅ AutoResearch program.md written. Open this folder in Claude/Cursor and tell the agent: 'Look at program.md and start the experiment loop.'",
        "note": "This is the real Karpathy autoresearch workflow"
    }
