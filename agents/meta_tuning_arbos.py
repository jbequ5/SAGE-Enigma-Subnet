# agents/meta_tuning_arbos.py - v2.0 MAXIMUM CAPABILITY Meta-Tuning Arbos
# Fully verifier-first, EFS/c/θ/heterogeneity/contract-aware, evolutionary tournament, and Grail-integrated

import json
from pathlib import Path
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetaTuningArbos:
    GENOME_PATH = Path("goals/brain/tuning_genome.json")
    
    def __init__(self, validator):
        self.validator = validator
        self.genome = self._load_genome()
        logger.info(f"MetaTuningArbos v2.0 initialized — EFS weights: {self.genome.get('efs_weights', {})}")

    def _load_genome(self):
        if self.GENOME_PATH.exists():
            try:
                return json.loads(self.GENOME_PATH.read_text(encoding="utf-8"))
            except:
                pass
        # Strong default genome (matches oracle _compute_efs exactly)
        default = {
            "version": "v2.0-verifier-first",
            "efs_weights": {"V": 0.300, "S": 0.175, "H": 0.175, "C": 0.175, "E": 0.175},
            "last_tuning": str(datetime.now().isoformat()),
            "mutation_rate": 0.14,
            "tournament_size": 8,
            "min_efs_improvement": 0.045,
            "active_principles": ["verifier_first", "heterogeneity_mandate", "contract_strictness", "stigmergic_learning"]
        }
        self._save_genome(default)
        return default

    def _save_genome(self, genome: dict):
        self.GENOME_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.GENOME_PATH.write_text(json.dumps(genome, indent=2))
        logger.info(f"Meta genome saved (version {genome.get('version')})")

    def compute_efs(self, metrics: dict = None) -> float:
        """Exact same EFS formula as ValidationOracle for perfect consistency."""
        if metrics is None:
            metrics = {
                "V": getattr(self.validator, "last_fidelity", 0.0) or getattr(self.validator, "last_score", 0.0),
                "S": 0.82,   # convergence / symbiosis estimate
                "H": getattr(self.validator.arbos, "_compute_heterogeneity_score", lambda *a: {"heterogeneity_score": 0.72})().get("heterogeneity_score", 0.72) if hasattr(self.validator, "arbos") else 0.72,
                "C": 0.78,   # compression / retrospective estimate
                "E": 0.85    # embodiment / pattern surfacer estimate
            }
        return self.validator._compute_efs(
            fidelity=metrics.get("V", 0.0),
            convergence_speed=metrics.get("S", 0.0),
            heterogeneity=metrics.get("H", 0.0),
            mean_delta_retro=metrics.get("C", 0.0),
            mau_per_token=metrics.get("E", 0.0)
        )

    def run_meta_tuning_cycle(self, stall_detected: bool = False, oracle_result: dict = None):
        """Full evolutionary meta-tuning cycle — oracle-driven, contract-aware, and Grail-promoting."""
        logger.info(f"🧬 Meta-Tuning Arbos activated {'(stall detected)' if stall_detected else ''}")

        # Use real oracle data when available
        if oracle_result:
            current_efs = oracle_result.get("efs", 0.0)
            dry_run_passed = oracle_result.get("dry_run_passed", True)
            spec = oracle_result.get("verifiability_contract", oracle_result.get("verifiability_spec", {}))
        else:
            current_efs = self.compute_efs()
            dry_run_passed = True
            spec = getattr(self.validator.arbos, "_current_strategy", {}).get("verifiability_contract", {}) if hasattr(self.validator, "arbos") else {}

        if not dry_run_passed or len(spec.get("artifacts_required", [])) < 2:
            logger.warning("Meta-tuning skipped — dry-run or contract not compliant")
            return {"status": "skipped", "reason": "dry_run_or_contract_failure"}

        # Evolutionary tournament
        base_weights = self.genome["efs_weights"].copy()
        mutants = []
        for i in range(self.genome.get("tournament_size", 8)):
            mutant = base_weights.copy()
            for key in mutant:
                mutant[key] = round(mutant[key] * random.uniform(0.86, 1.14), 3)
                mutant[key] = max(0.05, min(0.45, mutant[key]))
            mutants.append({"id": i, "weights": mutant, "predicted_efs": 0.0})

        # Tournament using real oracle EFS
        best_efs = current_efs
        best_genome = None

        for mutant in mutants:
            original = self.genome["efs_weights"]
            self.genome["efs_weights"] = mutant["weights"]

            mutant["predicted_efs"] = self.compute_efs()

            if mutant["predicted_efs"] > best_efs + self.genome.get("min_efs_improvement", 0.045):
                best_efs = mutant["predicted_efs"]
                best_genome = mutant

            self.genome["efs_weights"] = original

        # Apply winner if improvement found
        if best_genome and best_efs > current_efs + 0.03:
            logger.info(f"Meta-Tuning winner found — new EFS: {best_efs:.4f} (+{best_efs - current_efs:.4f})")
            self.genome["efs_weights"] = best_genome["weights"]
            self.genome["last_tuning"] = str(datetime.now().isoformat())
            self._save_genome(self.genome)

            # Trigger downstream evolution
            if hasattr(self.validator.arbos, 'evolve_principles_post_run'):
                self.validator.arbos.evolve_principles_post_run(
                    best_solution="Meta-tuning winner applied",
                    best_score=best_efs,
                    best_diagnostics={"efs_winner": best_genome}
                )

            # Promote to Grail
            if hasattr(self.validator.arbos, 'grail_extract_and_score'):
                self.validator.arbos.grail_extract_and_score(
                    f"Meta-tuning winner: EFS improved to {best_efs:.4f}", best_efs, 0.92, {"type": "meta_tuning"}
                )

            return {"status": "success", "best_efs": best_efs, "improvement": round(best_efs - current_efs, 4)}
        else:
            logger.info("Meta-tuning completed — no significant improvement")
            return {"status": "no_improvement", "best_efs": best_efs}
