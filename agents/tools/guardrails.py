# agents/tools/guardrails.py
# Hard safety checks before submission - integrated with ResourceMonitor

from agents.tools.resource_aware import ResourceMonitor

def apply_guardrails(solution: str, monitor: ResourceMonitor = None) -> str:
    """
    Applies all critical subnet guardrails.
    Returns the solution if it passes, otherwise a rejection message.
    """
    if monitor is None:
        monitor = ResourceMonitor(max_hours=3.8)

    elapsed = monitor.elapsed_hours()

    # 1. Hard H100 time limit
    if elapsed > 4.0:
        return f"REJECTED: Exceeds 4h H100 limit (elapsed: {elapsed:.2f}h)"

    # 2. Minimum solution length
    if len(solution.strip()) < 200:
        return "REJECTED: Solution too short (< 200 characters)"

    # 3. No obvious error messages
    error_keywords = ["error", "failed", "exception", "traceback", "timeout", "crashed"]
    if any(kw in solution.lower() for kw in error_keywords):
        return "REJECTED: Output contains error messages"

    # 4. Basic safety / hallucination check
    if "i don't know" in solution.lower() or "unable to" in solution.lower() and len(solution) < 500:
        return "REJECTED: Solution appears incomplete or uncertain"

    print(f"✅ All guardrails passed (elapsed: {elapsed:.2f}h / 4.0h)")
    return solution
