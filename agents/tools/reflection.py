# agents/tools/reflection.py
# Reflection pattern - Agent self-critiques and improves its output

def reflect_and_improve(task: str, output: str, llm, max_iterations: int = 4):
 """
 Reflection pattern from Agentic Design Patterns book.
 Agent generates → critiques → revises → loops until good.
 """
 current = output
 for i in range(max_iterations):
 critique = llm(f"""
 Task: {task}
 Output: {current}
 
 Critique: Check accuracy, completeness, logic, hallucinations, clarity.
 If perfect, reply ONLY "APPROVED".
 Otherwise list specific issues and fixes.
 """)
 
 if "APPROVED" in critique.upper():
 return current, critique
 
 # Revise based on critique
 current = llm(f"Improve the output based on this critique:\nCritique: {critique}\nOriginal: {current}")
 
 return current, "Max iterations reached" 
