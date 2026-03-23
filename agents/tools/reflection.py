# agents/tools/reflection.py
# Full Reflection pattern - self-critique and iterative improvement

def reflect_and_improve(task: str, output: str, llm_call, max_iterations: int = 4):
    """
    Reflection Pattern (Chapter 4 from Agentic Design Patterns book)
    Agent generates → self-critiques → revises → loops until good.
    """
    current = output
    trace = []

    for i in range(max_iterations):
        critique = llm_call(f"""
            Task: {task}
            Current Output: {current}
            
            Critique this output for:
            - Accuracy & correctness
            - Completeness
            - Logical gaps or hallucinations
            - Clarity & structure
            - Runtime feasibility (must stay under 4h H200)
            
            Reply ONLY with "APPROVED" if perfect, otherwise list specific fixes.
        """)
        
        trace.append({"iteration": i+1, "critique": critique[:200]})

        if "APPROVED" in critique.upper():
            return current, trace
        
        # Revise based on critique
        current = llm_call(f"Improve the previous output based on this critique:\nCritique: {critique}\nOriginal: {current}")
    
    return current, trace
