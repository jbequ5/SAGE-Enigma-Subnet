import re
from pathlib import Path
from typing import Dict, Any

class VerificationAnalyzer:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_content = self._load_goal(goal_file)

    def _load_goal(self, path: str) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except:
            return ""

    def analyze(self, verification_instructions: str = "", challenge: str = "") -> Dict[str, Any]:
        full_text = f"{self.goal_content}\n{verification_instructions}\n{challenge}"
        text_lower = full_text.lower()

        strategy = {
            "domain": "adaptive",
            "enabled_modules": ["sympy"],
            "scoring_weights": {
                "symbolic": 0.40,
                "deterministic": 0.35,
                "novelty": 0.15,
                "realism": 0.10,      # realism weight — feeds into SOTA rubric
                "speed": 0.0
            },
            "self_check_commands": [],
            "recommended_tools": [],
            "verification_type": "custom",
            "verifier_code_snippets": [],
            "difficulty_level": "medium",
            "requires_deterministic_first": True,
            # v0.6 additions for hybrid ingestion & pattern surfacing awareness
            "hybrid_ingestion_hints": [],
            "pattern_surfacing_hints": []
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

        strategy["recommended_tools"] = list(dict.fromkeys(strategy["recommended_tools"]))  # dedup

        # 4. Auto-detect difficulty level
        difficulty_keywords = {
            "high": ["break", "crack", "decrypt", "bitcoin", "btc", "rsa", "private key", "collision", "preimage", "invert", "solve for", "quantum", "shor", "grover", "post-quantum"],
            "medium": ["optimize", "quantum", "circuit", "simulation", "large scale", "complex", "cryptographic", "hash"],
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
        if strategy["verifier_code_snippets"] or any(t in text_lower for t in ["sympy", "deterministic", "verifier", "assert"]):
            strategy["requires_deterministic_first"] = True
        else:
            strategy["requires_deterministic_first"] = False

        # 6. v0.6 hybrid ingestion & pattern surfacing hints (lightweight)
        if any(k in text_lower for k in ["evoagent", "sakana", "genome", "paper", "archive"]):
            strategy["hybrid_ingestion_hints"].append("external_genome_detected")
        if any(k in text_lower for k in ["resonance", "photoelectric", "microtubule", "kruse", "pattern", "invariant cluster"]):
            strategy["pattern_surfacing_hints"].append("multi_scale_pattern_opportunity")

        return strategy
