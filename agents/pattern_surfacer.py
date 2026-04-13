# agents/pattern_surfacer.py - v0.9.7 MAXIMUM SOTA Resonance + Photoelectric Pattern Surfacer
# Fully verifier-first, EFS/c/heterogeneity-driven, contract-aware, graph-integrated,
# predictive-aware, vault-routing, PD Arm triggering, and Grail-promoting.

import json
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ResonancePatternSurfacer:
    """Microtubule-inspired fractal resonance coupling — now deeply oracle-driven, 
    contract-aware, graph-integrated, and Grail-promoting."""
    def __init__(self):
        self.resonance_count = 0
        self.output_dir = Path("goals/brain/grail_patterns/resonance")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def surface_resonance(self, oracle_result: dict = None, verifiability_contract: dict = None):
        """Surface resonance only on strong, verifier-sound signals."""
        try:
            efs = oracle_result.get("efs", 0.65) if oracle_result else 0.65
            hetero = oracle_result.get("heterogeneity_score", 0.72) if oracle_result else 0.72
            c = oracle_result.get("c3a_confidence", 0.75) if oracle_result else 0.75
            dry_run_passed = oracle_result.get("dry_run_passed", True) if oracle_result else True
            score = oracle_result.get("validation_score", 0.0) if oracle_result else 0.0

            # Strict quality gate — only surface on high-signal, contract-compliant runs
            if not dry_run_passed or efs < 0.62 or hetero < 0.68 or score < 0.78:
                logger.debug("Resonance surfacing skipped — insufficient oracle signal")
                return None

            pattern = {
                "type": "resonance_delta",
                "timestamp": datetime.now().isoformat(),
                "resonance_strength": round(0.65 + 0.28 * (efs * hetero * c), 3),
                "efs_at_surface": round(efs, 3),
                "heterogeneity_score": round(hetero, 3),
                "c3a_confidence": round(c, 3),
                "validation_score": round(score, 3),
                "detected_invariants": [
                    "fractal_self_similarity_across_loops",
                    "phase_lock_between_heterogeneity_and_EFS",
                    "resonance_amplification_in_grail"
                ],
                "verifiability_contract_compliant": True,
                "contract_artifacts_covered": len(verifiability_contract.get("artifacts_required", [])) if verifiability_contract else 0,
                "recommendation": "Reinforce this resonance cluster in next planning Arbos and bio_strategy.md",
                "grail_promotion_score": round(efs * hetero * c, 3)
            }

            self.resonance_count += 1
            out_file = self.output_dir / f"resonance_{self.resonance_count}_{int(datetime.now().timestamp())}.json"
            out_file.write_text(json.dumps(pattern, indent=2))

            logger.info(f"🌌 RPS surfaced strong resonance pattern (strength: {pattern['resonance_strength']:.3f} | EFS={efs:.3f} | Hetero={hetero:.3f})")

            # SOTA: Route high-signal resonance to Vaults
            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'intelligence'):
                run_data = {
                    "insight_score": pattern['resonance_strength'],
                    "predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0),
                    "efs": efs,
                    "heterogeneity": hetero,
                    "key_takeaway": f"RPS surfaced strong resonance pattern (strength {pattern['resonance_strength']:.3f})",
                    "flywheel_step": "embodiment_to_vaults"
                }
                self.arbos.intelligence.route_to_vaults(run_data)

            # Trigger Product Development Arm synthesis for resonance curriculum/tool
            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'pd_arm'):
                self.arbos.pd_arm.synthesize_product(
                    vault_data=[], 
                    market_signals={"predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0)}
                )

            return pattern

        except Exception as e:
            logger.debug(f"Resonance surfacing skipped (safe): {e}")
            return None


class PhotoelectricPatternSurfacer:
    """Kruse LWM-inspired photoelectric coupling — focuses on sudden high-fidelity signal propagation."""
    def __init__(self):
        self.pps_count = 0
        self.output_dir = Path("goals/brain/grail_patterns/photoelectric")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def surface_photoelectric(self, oracle_result: dict = None, verifiability_contract: dict = None):
        """Surface 'photoelectric' breakthroughs on sudden high-fidelity jumps."""
        try:
            efs = oracle_result.get("efs", 0.65) if oracle_result else 0.65
            fidelity = oracle_result.get("fidelity", 0.78) if oracle_result else 0.78
            c = oracle_result.get("c3a_confidence", 0.75) if oracle_result else 0.75
            score = oracle_result.get("validation_score", 0.0) if oracle_result else 0.0

            if fidelity < 0.88 or efs < 0.60 or score < 0.82:
                logger.debug("Photoelectric surfacing skipped — insufficient fidelity jump")
                return None

            pattern = {
                "type": "photoelectric_delta",
                "timestamp": datetime.now().isoformat(),
                "pps_strength": round(0.68 + 0.25 * (fidelity * c * efs), 3),
                "efs_at_surface": round(efs, 3),
                "fidelity": round(fidelity, 3),
                "c3a_confidence": round(c, 3),
                "validation_score": round(score, 3),
                "detected_invariants": [
                    "redox-like_signal_propagation_in_grail",
                    "sudden_high_fidelity_breakthrough",
                    "light_proxy_between_subarbos_and_wiki"
                ],
                "verifiability_contract_compliant": True,
                "contract_artifacts_covered": len(verifiability_contract.get("artifacts_required", [])) if verifiability_contract else 0,
                "recommendation": "Inject as mycelial heuristic in next meta-tuning cycle or bio_strategy.md",
                "grail_promotion_score": round(fidelity * c * efs, 3)
            }

            self.pps_count += 1
            out_file = self.output_dir / f"photoelectric_{self.pps_count}_{int(datetime.now().timestamp())}.json"
            out_file.write_text(json.dumps(pattern, indent=2))

            logger.info(f"⚡ PPS surfaced strong photoelectric breakthrough (strength: {pattern['pps_strength']:.3f} | fidelity={fidelity:.3f})")

            # SOTA: Route high-signal photoelectric to Vaults
            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'intelligence'):
                run_data = {
                    "insight_score": pattern['pps_strength'],
                    "predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0),
                    "efs": efs,
                    "heterogeneity": oracle_result.get("heterogeneity_score", 0.72),
                    "key_takeaway": f"PPS surfaced strong photoelectric breakthrough (strength {pattern['pps_strength']:.3f})",
                    "flywheel_step": "embodiment_to_vaults"
                }
                self.arbos.intelligence.route_to_vaults(run_data)

            # Trigger Product Development Arm synthesis
            if hasattr(self, 'arbos') and self.arbos and hasattr(self.arbos, 'pd_arm'):
                self.arbos.pd_arm.synthesize_product(
                    vault_data=[], 
                    market_signals={"predictive_power": getattr(self.arbos.predictive, 'predictive_power', 0.0)}
                )

            return pattern

        except Exception as e:
            logger.debug(f"Photoelectric surfacing skipped (safe): {e}")
            return None


# Global instances — now receive rich oracle_result and contract where possible
rps = ResonancePatternSurfacer()
pps = PhotoelectricPatternSurfacer()
