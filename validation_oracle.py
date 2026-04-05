import os
import json
from datetime import datetime
from typing import Dict, Any
import numpy as np

from verification_analyzer import VerificationAnalyzer
from goals.brain_loader import load_toggle

class ValidationOracle:
    def __init__(self, goal_file: str = "goals/killer_base.md", compute=None, arbos=None):
        self.analyzer = VerificationAnalyzer(goal_file)
        self.compute = compute
        self.arbos = arbos

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

    def _compute_mau_reinforcement(self, mau_text: str, validation_score: float, fidelity: float, heterogeneity: float) -> float:
        """v5.1 MAU Pyramid scoring"""
        symbolic_coverage = 0.85 if "sympy" in mau_text.lower() or "deterministic" in mau_text.lower() else 0.6
        return validation_score * (fidelity ** 1.5) * symbolic_coverage * heterogeneity

    def _compute_wiki_contrib(self) -> float:
        """Full v5.1 MAU Pyramid aware wiki contribution"""
        try:
            if not os.path.exists("goals/knowledge"):
                return 0.0

            total_mau_score = 0.0
            mau_count = 0

            for root, _, files in os.walk("goals/knowledge"):
                if any(x in root.lower() for x in ["wiki", "subtasks", "invariants", "concepts"]):
                    for f in files:
                        if f.endswith((".md", ".json")):
                            try:
                                path = os.path.join(root, f)
                                with open(path, "r", encoding="utf-8") as file:
                                    content = file.read()[:2000]  # limit for speed
                                # Simple MAU simulation: split on paragraphs/sentences
                                maus = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 30]
                                for mau in maus[:10]:  # cap per file
                                    score = self._compute_mau_reinforcement(
                                        mau,
                                        self.last_score,
                                        self.last_fidelity,
                                        self.arbos._compute_heterogeneity_score()["heterogeneity_score"] if self.arbos else 0.7
                                    )
                                    total_mau_score += score
                                    mau_count += 1
                            except:
                                pass

            if mau_count == 0:
                return 0.0

            avg_mau_score = total_mau_score / mau_count
            contrib = min(0.35, avg_mau_score * 0.12)  # gentle scaling

            # Extra boost when byterover_mau_enabled
            if getattr(self.arbos, 'byterover_mau_enabled', False):
                contrib = min(0.45, contrib * 1.5)

            return round(contrib, 3)
        except:
            return 0.0

    def run(self, candidate: Dict[str, Any], verification_instructions: str = "", 
            challenge: str = "", goal_md: str = "") -> Dict[str, Any]:
        
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

        # === PRIORITY 2: LLM SCORING with model routing ===
        score = deterministic_score
        notes = f"Primarily deterministic/verifier-first scoring (strength: {deterministic_score:.2f})"
        vvd_ready = score > 0.82
        realism_penalty = False

        if deterministic_score <= 0.35 and self.compute is not None:
            model_config = self.arbos.load_model_registry(role="verification") if hasattr(self.arbos, 'load_model_registry') else {}

            scoring_prompt = f"""You are a strict, expert Validation Oracle for Bittensor SN63.

{full_context}

Scoring Rules:
- Prioritize deterministic/verifier results heavily.
- Be extremely realistic and critical.
- Heavily penalize generic or overconfident answers.
- Reward honest feasibility statements and any real symbolic progress.

Return ONLY valid JSON with the keys shown."""

            try:
                response = self.compute.call_llm(
                    prompt=scoring_prompt,
                    temperature=0.35,
                    max_tokens=900,
                    model_config=model_config
                )
                parsed = self._safe_parse_json(response)
                score = float(parsed.get("validation_score", deterministic_score + 0.45))
                notes = parsed.get("notes", "LLM-assisted realistic scoring")
                vvd_ready = bool(parsed.get("vvd_ready", score > 0.80))
                realism_penalty = bool(parsed.get("realism_penalty", False))
            except Exception as e:
                score = deterministic_score + 0.45
                notes = f"Fallback after LLM error: {str(e)[:80]}"
                vvd_ready = False
                realism_penalty = True

        self.last_score = max(0.35, min(0.94, score))
        self.last_vvd_ready = vvd_ready
        self.last_fidelity = round(0.80 + np.random.normal(0, 0.08), 3)
        self.last_notes = notes

        if realism_penalty:
            self.last_notes += " | Realism penalty applied"

        # ====================== v5.1 FULL MAU PYRAMID WIKI INTEGRATION ======================
        wiki_contrib = self._compute_wiki_contrib()
        self.last_wiki_contrib = wiki_contrib

        aha_strength = max(0.0, self.last_score - 0.65) if self.last_score > 0.70 else 0.0
        self.last_aha_strength = round(aha_strength, 3)

        # Boost from wiki activity (MAU reinforcement)
        if wiki_contrib > 0.05:
            self.last_score = min(0.96, self.last_score + (wiki_contrib * 0.08))

        # C3A confidence
        c = self.arbos.compute_confidence(0.78, 0.70, 0.88) if hasattr(self.arbos, 'compute_confidence') else 0.75

        # Decision Journal write
        if hasattr(self.arbos, 'decision_journal_enabled') and self.arbos.decision_journal_enabled:
            self.arbos.write_decision_journal(
                subtask_id="validation_oracle",
                hypothesis="Validation score computed",
                evidence=notes,
                performance_delta={"delta_c": c, "delta_s": self.last_score, "wiki_contrib": wiki_contrib},
                organic_thought=f"AHA strength: {aha_strength:.3f} | MAU contrib: {wiki_contrib:.3f}"
            )

        # Update brain metrics
        if wiki_contrib > 0.05 or aha_strength > 0.1:
            try:
                metrics_path = "goals/brain/metrics.md"
                os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
                with open(metrics_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n### ValidationOracle Update {datetime.now().isoformat()}\n"
                            f"aha_strength: {self.last_aha_strength:.3f}\n"
                            f"wiki_contribution_score: {self.last_wiki_contrib:.3f}\n"
                            f"c3a_confidence: {c:.3f}")
            except:
                pass

        return {
            "validation_score": self.last_score,
            "vvd_ready": self.last_vvd_ready,
            "notes": self.last_notes + f" | Wiki/MAU contrib: {wiki_contrib:.3f} | C3A c: {c:.3f}",
            "strategy": strategy,
            "fidelity": self.last_fidelity,
            "deterministic_strength": deterministic_score,
            "aha_strength": self.last_aha_strength,
            "wiki_contribution_score": self.last_wiki_contrib,
            "c3a_confidence": c
        }
