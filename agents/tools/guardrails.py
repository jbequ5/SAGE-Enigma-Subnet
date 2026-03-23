# agents/tools/guardrails.py
# Guardrails - safety checks before submission

def apply_guardrails(solution: str, runtime_hours: float):
    """Enforces quality, runtime, and validity"""
    if runtime_hours > 4.0:
        return "REJECTED: Exceeds 4h H100 limit"
    if len(solution) < 50:
        return "REJECTED: Solution too short"
    return "PASSED"
