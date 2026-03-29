import re
from pathlib import Path
from typing import Dict, Any

class VerificationAnalyzer:
    def __init__(self, goal_file: str = "goals/killer_base.md"):
        self.goal_content = self._load_goal(goal_file)

    def _load_goal(self, path: str) -> str:
        try:
            return Path(path).read_text()
        except:
            return ""

    def analyze(self, verification_instructions: str = "", challenge: str = "") -> Dict[str, Any]:
        text = f"{self.goal_content}\n{verification_instructions}\n{challenge}".lower()

        strategy = {
            "domain": "general",
            "enabled_modules": ["sympy"],
            "scoring_weights": {"fidelity": 0.07, "symbolic": 0.05, "speed": 0.03, "fingerprint": 0.0},
            "self_check_commands": [],
            "recommended_tools": [],
            "verification_type": "standard"
        }

        if any(k in text for k in ["fingerprint", "synthetic circuit", "proof of compute", "statistical", "peaked circuit"]):
            strategy["domain"] = "quantum_sn63"
            strategy["enabled_modules"] = ["stim", "pytket", "quantum_rings", "sympy"]
            strategy["recommended_tools"] = ["stim", "pytket"]
            strategy["scoring_weights"]["fidelity"] = 0.15
            strategy["scoring_weights"]["fingerprint"] = 0.12
            strategy["verification_type"] = "fingerprint_proof"

        elif any(k in text for k in ["stim", "tableau", "pauli", "stabilizer", "fidelity", "quantum rings", "circuit"]):
            strategy["domain"] = "quantum"
            strategy["enabled_modules"] = ["stim", "pytket", "quantum_rings", "sympy"]
            strategy["recommended_tools"] = ["stim", "pytket"]
            strategy["scoring_weights"]["fidelity"] = 0.12
            strategy["scoring_weights"]["symbolic"] = 0.08

        elif any(k in text for k in ["sympy", "algebra", "equation", "matrix"]):
            strategy["domain"] = "math"
            strategy["enabled_modules"] = ["sympy"]

        elif any(k in text for k in ["crypto", "zk", "ecc", "rsa"]):
            strategy["domain"] = "crypto"
            strategy["enabled_modules"] = ["sympy"]

        checks = re.findall(r'(?:self_check|verify|validate|assert|fingerprint|statistical).*?```python(.*?)```', verification_instructions + challenge, re.DOTALL | re.IGNORECASE)
        strategy["self_check_commands"] = [c.strip() for c in checks if c.strip()]

        return strategy
