# agents/tools/guardrails.py - v2.0 SOTA Guardrails
# Hard safety checks before submission - integrated with ResourceMonitor, EFS, C3A, 
# approximation mode, and embodiment awareness

from agents.tools.resource_aware import ResourceMonitor
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def apply_guardrails(solution: str, monitor: ResourceMonitor = None, context: Dict = None) -> Dict[str, Any]:
    """
    Applies all critical guardrails before accepting a solution.
    Returns a dict with pass/fail status and clear reason.
    """
    if monitor is None:
        monitor = ResourceMonitor(max_hours=3.8)

    if context is None:
        context = {}

    result = {
        "passed": True,
        "reason": "All guardrails passed",
        "severity": "none",
        "recommendation": "ACCEPT"
    }

    elapsed = monitor.elapsed_hours()

    # 1. Hard time / resource limits
    if elapsed > 4.0:
        return {
            "passed": False,
            "reason": f"Exceeds 4h compute limit (elapsed: {elapsed:.2f}h)",
            "severity": "critical",
            "recommendation": "REJECT"
        }

    if len(solution.strip()) < 150:
        return {
            "passed": False,
            "reason": "Solution too short (< 150 characters) — likely incomplete or empty",
            "severity": "high",
            "recommendation": "REJECT"
        }

    solution_lower = solution.lower()

    # 2. Error / crash detection
    error_keywords = ["traceback", "exception", "error:", "failed", "crashed", "oom", "out of memory", "runtimeerror", "timeout"]
    if any(kw in solution_lower for kw in error_keywords):
        return {
            "passed": False,
            "reason": "Output contains error messages or failure indicators",
            "severity": "high",
            "recommendation": "REJECT"
        }

    # 3. Uncertainty / hallucination check (only penalize if very short)
    uncertainty_phrases = ["i don't know", "unable to", "not sure", "cannot determine", "insufficient information"]
    if any(phrase in solution_lower for phrase in uncertainty_phrases) and len(solution) < 500:
        return {
            "passed": False,
            "reason": "Solution appears uncertain or incomplete",
            "severity": "medium",
            "recommendation": "REJECT"
        }

    # 4. Verifier / SOTA alignment check
    if "validation_score" in solution_lower and "0.0" in solution_lower:
        return {
            "passed": False,
            "reason": "Solution contains obvious zero-score or failure indicators",
            "severity": "high",
            "recommendation": "REJECT"
        }

    # 5. v0.8+ SOTA / EFS / Embodiment-aware checks
    if context.get("sota_gate_passed") is False:
        return {
            "passed": False,
            "reason": "Failed SOTA partial-credit gate or dynamic θ_dynamic check",
            "severity": "high",
            "recommendation": "REJECT"
        }

    if context.get("efs", 0.0) < 0.45 and len(solution) < 800:
        return {
            "passed": False,
            "reason": f"Extremely low EFS ({context.get('efs', 0.0):.3f}) on short solution",
            "severity": "medium",
            "recommendation": "REJECT"
        }

    # 6. Approximation mode warning (soft)
    if context.get("approximation_used", False):
        result["notes"] = "Solution used approximation mode due to missing backend"
        result["severity"] = "low"

    logger.info(f"Guardrails passed for solution ({len(solution)} chars) | EFS: {context.get('efs', 'N/A')}")
    return result
