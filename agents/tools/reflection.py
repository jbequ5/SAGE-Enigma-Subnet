# agents/tools/reflection.py
# Full Reflection Pattern - self-critique and iterative improvement

from agents.tools.hyperagent import run_hyperagent

def reflect_and_improve(task: str, output: str, max_iterations: int = 3):
    """
    Reflection Pattern using HyperAgent as the LLM caller.
    Critiques → Revises → Stops when APPROVED or max iterations reached.
    """
    current = output
    trace = []

    for i in range(max_iterations):
        critique_task = f"""
Task: {task}
Current Output: {current}

Critique this output on:
- Accuracy
- Completeness
- Logical consistency
- Hallucinations
- Clarity
- Alignment with original goal
- H100 runtime feasibility

Reply ONLY with "APPROVED" if it is excellent. Otherwise give specific, actionable fixes.
"""

        critique_result = run_hyperagent(task=critique_task, parallel_tasks=2)
        critique = critique_result.get("output", "")

        trace.append({"iteration": i + 1, "critique": critique[:400]})

        if "APPROVED" in critique.upper():
            print(f"✅ Reflection approved after {i+1} iterations")
            return current, trace

        # Revise the output
        revise_task = f"""
Improve the following output based on this critique:

Critique: {critique}

Original Output: {current}

Produce a revised, higher-quality version.
"""

        revise_result = run_hyperagent(task=revise_task, parallel_tasks=2)
        current = revise_result.get("output", current)

    print(f"⚠️  Reflection reached max iterations ({max_iterations})")
    return current, trace
