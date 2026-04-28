import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class VerificationAnalyzer:
    """SOTA VerificationAnalyzer — single source of truth for challenge analysis, verifier-first contract creation, 7D signals, and deterministic-first hints."""

    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_content = self._load_goal(goal_file)
        logger.info(f"✅ VerificationAnalyzer v0.9.13+ SOTA initialized — goal file: {goal_file}")

    def _load_goal(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not load goal file {path} (safe fallback): {e}")
            return ""

    def analyze(self, verification_instructions: str = "", challenge: str = "") -> Dict[str, Any]:
        """Full SOTA analysis: extracts code, tools, difficulty, and generates machine-readable verifiability contract."""
        full_text = f"{self.goal_content}\n{verification_instructions}\n{challenge}"
        text_lower = full_text.lower()

        strategy = {
            "domain": "adaptive",
            "enabled_modules": ["sympy", "pulp", "scipy", "networkx", "z3"],
            "scoring_weights": {
                "symbolic": 0.40,
                "deterministic": 0.35,
                "novelty": 0.15,
                "realism": 0.10,
                "speed": 0.0
            },
            "self_check_commands": [],
            "recommended_tools": [],
            "verification_type": "custom",
            "verifier_code_snippets": [],
            "difficulty_level": "medium",
            "requires_deterministic_first": True,
            "hybrid_ingestion_hints": [],
            "pattern_surfacing_hints": [],
            "verifier_quality_signals": {}
        }

        # 1. Extract verifier code blocks (highest priority)
        code_blocks = re.findall(r'```(?:python|py|code)?\s*(.*?)```', full_text, re.DOTALL | re.IGNORECASE)
        strategy["verifier_code_snippets"] = [b.strip() for b in code_blocks if b.strip() and len(b.strip()) > 10]

        # 2. Extract self-check / validation commands
        check_patterns = [
            r'(?:self[-_]?check|verify|validate|assert|score|metric|test).*?```(?:python|py)?\s*(.*?)```',
            r'(?:check|verify|validate).*?(?:```|\n\s*def\s+\w+|\n\s*assert)',
        ]
        for pattern in check_patterns:
            checks = re.findall(pattern, full_text, re.DOTALL | re.IGNORECASE)
            strategy["self_check_commands"].extend([c.strip() for c in checks if c.strip()])

        # 3. Extract recommended tools / libraries (deterministic first)
        tool_patterns = [
            r'(?:use|install|require|pip install|from|import)\s+([a-z0-9\-_]+)',
            r'(?:library|package|module|tool):\s*([a-z0-9\-_]+)'
        ]
        for pattern in tool_patterns:
            tools = re.findall(pattern, text_lower)
            strategy["recommended_tools"].extend(tools)
        strategy["recommended_tools"] = list(dict.fromkeys(strategy["recommended_tools"]))

        # 4. Auto-detect difficulty level
        difficulty_keywords = {
            "high": ["break", "crack", "decrypt", "bitcoin", "btc", "rsa", "private key", "collision", "preimage", "invert", "solve for", "quantum", "shor", "grover", "post-quantum", "np-hard", "undecidable"],
            "medium": ["optimize", "quantum", "circuit", "simulation", "large scale", "complex", "cryptographic", "hash", "stabilizer", "invariant"],
            "low": ["simple", "basic", "hello", "example", "demo"]
        }
        difficulty_score = 0
        for level, keywords in difficulty_keywords.items():
            if any(kw in text_lower for kw in keywords):
                if level == "high":
                    difficulty_score += 2
                elif level == "medium":
                    difficulty_score += 1
        if difficulty_score >= 2:
            strategy["difficulty_level"] = "high"
        elif difficulty_score == 1:
            strategy["difficulty_level"] = "medium"
        else:
            strategy["difficulty_level"] = "low"

        # 5. Flag if deterministic tooling should be prioritized
        if strategy["verifier_code_snippets"] or any(t in text_lower for t in ["sympy", "deterministic", "verifier", "assert", "z3", "pulp"]):
            strategy["requires_deterministic_first"] = True

        # 6. Hybrid ingestion & pattern surfacing hints
        if any(k in text_lower for k in ["evoagent", "sakana", "genome", "paper", "archive", "huggingface"]):
            strategy["hybrid_ingestion_hints"].append("external_genome_detected")
        if any(k in text_lower for k in ["resonance", "photoelectric", "microtubule", "kruse", "pattern", "invariant cluster", "fractal"]):
            strategy["pattern_surfacing_hints"].append("multi_scale_pattern_opportunity")

        # 7. Generate full verifiability spec
        strategy["verifiability_spec"] = self._generate_verifiability_spec(challenge, verification_instructions)

        # 8. Populate 7D verifier quality signals
        strategy["verifier_quality_signals"] = {
            "edge_coverage_target": 0.75,
            "invariant_tightness_target": 0.70,
            "fidelity_target": 0.78,
            "c3a_confidence_target": 0.78,
            "theta_dynamic_gate": "passed",
            "efs_target": 0.65
        }

        logger.info(f"VerificationAnalyzer completed — difficulty: {strategy['difficulty_level']}, verifier snippets: {len(strategy['verifier_code_snippets'])}, deterministic first: {strategy['requires_deterministic_first']}")

        return strategy

    def _generate_verifiability_spec(self, challenge: str, instructions: str) -> Dict[str, Any]:
        """PhD-rigorous, machine-readable contract generated from every challenge."""
        return {
            "version": "1.1",
            "challenge_summary": challenge[:600],
            "artifacts_required": [],
            "composability_rules": [
                "No internal state contradictions between artifacts",
                "Clear merge interfaces defined in each artifact schema",
                "Merged candidate must be executable against full verifier_code_snippets",
                "All artifacts must contribute to at least one dry_run_success_criteria"
            ],
            "dry_run_success_criteria": {
                "edge_coverage": ">= 0.75",
                "invariant_tightness": ">= 0.70",
                "fidelity": ">= 0.78",
                "c3a_confidence": ">= 0.78",
                "theta_dynamic_gate": "passed",
                "EFS": ">= 0.65",
                "minimum_artifacts_covered": ">= 90%"
            },
            "learning_mandate": "Every dry-run and swarm outcome MUST write full trace (spec + grades + failures + real_delta) to wiki/trajectories for mycelial evolution",
            "heterogeneity_mandate": "Subtasks must explore all five axes (symbolic, numeric, linguistic, edge-case, invariant-tight)",
            "verifier_quality_signals": {
                "edge_coverage_target": 0.75,
                "invariant_tightness_target": 0.70,
                "fidelity_target": 0.78,
                "c3a_confidence_target": 0.78,
                "theta_dynamic_gate": "passed",
                "efs_target": 0.65
            }
        }
