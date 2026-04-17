# agents/tools/guardrails.py
# v0.9.11 MAXIMUM SOTA Guardrails
# Hard safety checks before submission - integrated with ResourceMonitor, EFS, C3A,
# θ_dynamic, verifier_quality (7D), predictive_power, approximation mode, and embodiment awareness.

from agents.tools.resource_aware import ResourceMonitor
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def apply_guardrails(solution: str, monitor: ResourceMonitor = None, context: Dict = None) -> Dict[str, Any]:
    """
    Applies all critical guardrails before accepting a solution.
    Returns a dict with pass/fail status, clear reason, severity, and recommendation.
    Fully SOTA-aware with EFS, 7D verifier signals, predictive power, and embodiment checks.
    """
    if monitor is None:
        monitor = ResourceMonitor(max_hours=3.8)
    if context is None:
        context = {}

    result = {
        "passed": True,
        "reason": "All guardrails passed",
        "severity": "none",
        "recommendation": "ACCEPT",
        "notes": ""
    }

    elapsed = monitor.elapsed_hours()
    efs = context.get("efs", 0.0)
    verifier_quality = context.get("verifier_quality", 0.0)
    predictive_power = context.get("predictive_power", 0.0)
    theta_dynamic = context.get("theta_dynamic", 0.0)
    approximation_used = context.get("approximation_used", False)
    embodiment_enabled = context.get("embodiment_enabled", True)

    solution_lower = solution.lower()
    solution_length = len(solution.strip())

    # 1. Hard time / resource limits
    if elapsed > 4.0:
        return {
            "passed": False,
            "reason": f"Exceeds 4h compute limit (elapsed: {elapsed:.2f}h)",
            "severity": "critical",
            "recommendation": "REJECT"
        }

    # 2. Solution too short / empty
    if solution_length < 150:
        return {
            "passed": False,
            "reason": "Solution too short (< 150 characters) — likely incomplete or empty",
            "severity": "high",
            "recommendation": "REJECT"
        }

    # 3. Error / crash detection
    error_keywords = ["traceback", "exception", "error:", "failed", "crashed", "oom", "out of memory", "runtimeerror", "timeout", "killed", "segfault"]
    if any(kw in solution_lower for kw in error_keywords):
        return {
            "passed": False,
            "reason": "Output contains error messages or failure indicators",
            "severity": "high",
            "recommendation": "REJECT"
        }

    # 4. Uncertainty / hallucination check (only penalize if very short or low EFS)
    uncertainty_phrases = ["i don't know", "unable to", "not sure", "cannot determine", "insufficient information", "no idea", "guess"]
    if any(phrase in solution_lower for phrase in uncertainty_phrases) and (solution_length < 600 or efs < 0.55):
        return {
            "passed": False,
            "reason": "Solution appears uncertain, incomplete, or hallucinatory",
            "severity": "high",
            "recommendation": "REJECT"
        }

    # 5. Verifier / SOTA alignment check
    if "validation_score" in solution_lower and "0.0" in solution_lower:
        return {
            "passed": False,
            "reason": "Solution contains obvious zero-score or failure indicators",
            "severity": "high",
            "recommendation": "REJECT"
        }

    # 6. SOTA / EFS / 7D Verifier Quality checks
    if context.get("sota_gate_passed") is False:
        return {
            "passed": False,
            "reason": "Failed SOTA partial-credit gate or dynamic θ_dynamic check",
            "severity": "high",
            "recommendation": "REJECT"
        }

    if efs < 0.45 and solution_length < 800:
        return {
            "passed": False,
            "reason": f"Extremely low EFS ({efs:.3f}) on short solution",
            "severity": "medium",
            "recommendation": "REJECT"
        }

    if verifier_quality < 0.65 and solution_length < 1000:
        return {
            "passed": False,
            "reason": f"Low verifier quality (7D): {verifier_quality:.3f}",
            "severity": "medium",
            "recommendation": "REJECT"
        }

    # 7. Approximation mode warning (soft but visible)
    if approximation_used:
        result["notes"] = "Solution used approximation mode due to missing deterministic backend"
        result["severity"] = "low"

    # 8. Embodiment awareness check
    if not embodiment_enabled and predictive_power < 0.60:
        result["notes"] += " | Embodiment disabled — lower confidence expected"

    # Final high-signal routing note
    if efs > 0.82 and predictive_power > 0.75:
        result["notes"] += " | High EFS + Predictive Power — strong candidate for VaultRouter + PD Arm"

    logger.info(f"Guardrails passed for solution ({solution_length} chars) | EFS: {efs:.3f} | VerifierQ: {verifier_quality:.3f} | Predictive: {predictive_power:.3f}")
    return result
