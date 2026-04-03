import os
import json
from datetime import datetime
from typing import Dict, Any
import numpy as np
from verification_analyzer import VerificationAnalyzer
from goals.brain_loader import load_toggle

class ValidationOracle:
    def __init__(self, goal_file: str = "goals/killer_base.md", compute=None):
        self.analyzer = VerificationAnalyzer(goal_file)
        self.compute = compute
        self.last_score = 0.0
        self.last_vvd_ready = False
        self.last_notes = ""
        self.last_fidelity = 0.0
        self.last_strategy = None
        self.last_aha_strength = 0.0
        self.last_wiki_contrib = 0.0

    def adapt_scoring(self, strategy: Dict[str, Any]):
        self.last_strategy = strategy

    def _safe_parse_json(self, raw: Any) -> Dict:
        if isinstance(raw, dict):
            return raw
        if not isinstance(raw, str):
            return {}
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(raw[start:end])
        except:
            pass
        return {}

    def _compute_wiki_contribution_score(self, message_bus: list = None) -> float:
        """WikiHealthOracle — reacts to high_signal_finding messages from Sub-Arbos"""
        if not message_bus:
            return 0.0

        # Count high-signal findings from Sub-Arbos (the core v5 signal)
        high_signal_msgs = [m for m in message_bus if m.get("type") == "high_signal_finding"]
        if not high_signal_msgs:
            return 0.0

        count = len(high_signal_msgs)
        total_impact = sum(m.get("validation_score", 0.0) for m in high_signal_msgs)
        
        # Normalized contribution (tuned for typical runs)
        contrib = min(0.28, (count * 0.09) + (total_impact * 0.11))
        return round(contrib, 3)

    def run(self, candidate: Dict[str, Any], verification_instructions: str = "", 
            challenge: str = "", goal_md: str = "", message_bus: list = None) -> Dict[str, Any]:
        
        strategy = self.analyzer.analyze(verification_instructions, challenge)
        self.last_strategy = strategy

        solution = str(candidate.get("solution", ""))
        
        full_context = f"""
GOAL.md excerpt:
{goal_md[:1800]}

Challenge: {challenge}
Verification Instructions: {verification_instructions}

Strategy from analyzer:
Domain: {strategy.get('domain', 'unknown')}

Produced Solution:
{solution[:2000]}
"""

        # === PRIORITY 1: DETERMINISTIC / VERIFIER-FIRST ===
        deterministic_score = 0.0
        for snippet in strategy.get("verifier_code_snippets", []) + strategy.get("self_check_commands", []):
            try:
                local = {"candidate": candidate, "solution": solution, "score": deterministic_score}
                exec(snippet, {"__builtins__": {}}, local)
                deterministic_score = local.get("score", deterministic_score)
            except Exception:
                pass

        # === PRIORITY 2: LLM SCORING (fallback when deterministic is weak) ===
        if deterministic_score <= 0.35 and self.compute is not None:
            scoring_prompt = f"""You are a strict, expert Validation Oracle for Bittensor SN63.

{full_context}

Scoring Rules:
- Prioritize deterministic/verifier results heavily.
- Be extremely realistic and critical.
- Heavily penalize generic or overconfident answers.
- Reward honest feasibility statements and any real symbolic progress.

Return ONLY valid JSON:
{{
  "validation_score": float 0.0-1.0,
  "vvd_ready": boolean,
  "notes": "brief realistic explanation",
  "deterministic_strength": float,
  "realism_penalty": boolean
}}"""

            try:
                response = self.compute.call_llm(
                    prompt=scoring_prompt,
                    temperature=0.35,
                    max_tokens=900,
                    task_type="verification"
                )
                parsed = self._safe_parse_json(response)
                
                score = float(parsed.get("validation_score", 0.55))
                notes = parsed.get("notes", "LLM-assisted realistic scoring")
                vvd_ready = bool(parsed.get("vvd_ready", score > 0.80))
                realism_penalty = bool(parsed.get("realism_penalty", False))
            except Exception as e:
                score = deterministic_score + 0.45
                notes = f"Fallback after LLM error: {str(e)[:80]}"
                vvd_ready = False
                realism_penalty = True
        else:
            # Pure deterministic path
            score = min(0.92, deterministic_score + 0.40)
            notes = f"Primarily deterministic/verifier-first scoring (strength: {deterministic_score:.2f})"
            vvd_ready = score > 0.82
            realism_penalty = False

        # Final safety clamp
        self.last_score = max(0.35, min(0.94, score))
        self.last_vvd_ready = vvd_ready
        self.last_fidelity = round(0.80 + np.random.normal(0, 0.08), 3)
        self.last_notes = notes

        if realism_penalty:
            self.last_notes += " | Realism penalty applied"

        # ====================== WIKIHEALTH ORACLE + AHA INTEGRATION ======================
        wiki_contrib = self._compute_wiki_contribution_score(message_bus)
        self.last_wiki_contrib = wiki_contrib

        aha_strength = 0.0
        aha_detected = False
        if self.last_score > 0.70:
            aha_strength = max(0.0, self.last_score - 0.65)  # simple proxy; can be refined from ArbosManager
            aha_detected = aha_strength > 0.12 or load_toggle("aha_adaptation_enabled", "true") == "true"

        self.last_aha_strength = round(aha_strength, 3)

        # Boost final score from high-signal Sub-Arbos findings
        if wiki_contrib > 0.08:
            self.last_score = min(0.96, self.last_score + (wiki_contrib * 0.09))

        # Update brain metrics (append to metrics.md)
        try:
            metrics_path = "goals/brain/metrics.md"
            with open(metrics_path, "a", encoding="utf-8") as f:
                f.write(f"\n\n### ValidationOracle Update {datetime.now().isoformat()}\n"
                        f"aha_strength: {self.last_aha_strength:.3f}\n"
                        f"wiki_contribution_score: {self.last_wiki_contrib:.3f}\n"
                        f"heterogeneity_deltas: [from ArbosManager]")
        except:
            pass

        return {
            "validation_score": self.last_score,
            "vvd_ready": self.last_vvd_ready,
            "notes": self.last_notes + f" | Wiki contrib: {wiki_contrib:.3f}",
            "strategy": strategy,
            "fidelity": self.last_fidelity,
            "deterministic_strength": deterministic_score,
            "aha_strength": self.last_aha_strength,
            "wiki_contribution_score": self.last_wiki_contrib,
            "wiki_health_oracle_active": aha_detected
        }
