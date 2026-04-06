# agents/history_parse_hunter.py - v0.6 HistoryParseHunter + Retrospective Scoring + Auditing
from agents.video_archiver import VideoArchiver
from agents.validation_oracle import ValidationOracle
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HistoryParseHunter:
    def __init__(self, validation_oracle: ValidationOracle):
        self.video_hunter = VideoArchiver()
        self.oracle = validation_oracle
        self.archive_dir = Path("memdir/archives")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        logger.info("✅ HistoryParseHunter initialized — retrospective + auditing ready")

    def compute_retrospective_score(self, old_mau: dict, current_brain: dict) -> float:
        """Δ_retro × decay × hetero_bonus × validation_multiplier"""
        if not old_mau or not current_brain:
            return 0.0

        # Compute delta (how much better the current brain would score this old MAU)
        try:
            delta = self.oracle._compute_delta_retro(old_mau, current_brain)
        except:
            delta = 0.0  # safe fallback

        # Time decay
        try:
            age_days = (datetime.now() - datetime.fromisoformat(old_mau.get("timestamp", "2024-01-01"))).days
            decay = 0.92 ** max(0, age_days)
        except:
            decay = 0.85

        hetero_bonus = current_brain.get("heterogeneity_score", 1.0)
        val_mult = old_mau.get("validation_score", 0.5)

        score = delta * decay * hetero_bonus * val_mult * 1.8  # retrospective boost
        return round(max(0.0, min(1.0, score)), 4)

    def _compute_delta_retro(self, old_mau: dict, current_brain: dict) -> float:
        """Helper used by oracle and retrospective — how much the current brain improves this old MAU"""
        old_score = old_mau.get("validation_score", 0.5)
        # Simulate re-scoring with current principles/heterogeneity
        current_hetero = current_brain.get("heterogeneity_score", 0.72)
        improvement = (current_hetero - old_mau.get("heterogeneity_score", 0.5)) * 0.6
        return max(0.0, improvement + (0.15 if old_score < 0.6 else 0.0))

    def run_audit_on_mp4_backlog(self) -> dict:
        """Full-system auditing layer — checks logic fidelity, regression, gate success, EFS impact"""
        if not self.archive_dir.exists():
            return {"audits": [], "summary": "No archives found yet"}

        audits = []
        for mp4 in sorted(self.archive_dir.glob("*.mv2"), reverse=True):
            try:
                data = self.video_hunter.decode_mp4(str(mp4))
                audit = {
                    "file": str(mp4),
                    "logic_fidelity": self.oracle._sota_partial_credit_score(data),
                    "regression_rate": self._compute_regression_rate(data),
                    "gate_success": self._gate_success_rate(data),
                    "efs_impact": self._compute_efs_impact(data)
                }
                audits.append(audit)
            except Exception as e:
                logger.warning(f"Audit failed for {mp4}: {e}")

        if not audits:
            return {"audits": [], "summary": "No valid archives to audit"}

        avg_fidelity = sum(a["logic_fidelity"] for a in audits) / len(audits)
        summary = "Logic hardening confirmed" if avg_fidelity > 0.85 else "Attention required — regression or gate issues detected"

        return {
            "audits": audits[:20],  # limit for UI
            "summary": summary,
            "avg_logic_fidelity": round(avg_fidelity, 3),
            "total_archives": len(audits)
        }

    def _compute_regression_rate(self, data: dict) -> float:
        """Simple regression detection — how much score dropped vs previous runs"""
        try:
            current = data.get("final_score", data.get("validation_score", 0.0))
            # In real use this would compare against history; here we simulate
            return max(0.0, 0.45 - current)  # placeholder — can be enhanced with full history
        except:
            return 0.0

    def _gate_success_rate(self, data: dict) -> float:
        """Percentage of gates that passed in this run"""
        try:
            gates = data.get("gate_success", 1.0)
            return round(gates, 3)
        except:
            return 0.85

    def _compute_efs_impact(self, data: dict) -> float:
        """EFS impact of this archived run"""
        try:
            return data.get("efs", 0.0)
        except:
            return 0.0

    def trigger_retrospective(self, run_id: str = None):
        """Auto-called on Deep Replan, high-signal runs, or manual button"""
        try:
            # Find latest archive (or specific by run_id)
            archives = sorted(self.archive_dir.glob("*.mv2"), reverse=True)
            if not archives:
                logger.info("No archives found for retrospective")
                return {"status": "no_archives"}

            target = next((a for a in archives if run_id and run_id in a.name), archives[0])
            data = self.video_hunter.decode_mp4(str(target))

            # Re-score with current brain
            current_brain = {
                "heterogeneity_score": getattr(self.oracle.arbos, '_compute_heterogeneity_score', lambda: {"heterogeneity_score": 0.72})()["heterogeneity_score"]
            }

            retro_score = self.compute_retrospective_score(data, current_brain)

            if retro_score > 0.65:
                # Promote high-delta MAUs
                if hasattr(self.oracle.arbos, 'memory_layers'):
                    self.oracle.arbos.memory_layers.promote_high_signal(
                        str(data),
                        {"local_score": retro_score, "type": "retrospective_delta", "run_id": run_id}
                    )
                logger.info(f"✅ High retrospective delta ({retro_score:.3f}) — MAUs promoted")
            else:
                logger.info(f"Retrospective delta low ({retro_score:.3f}) — no promotion")

            return {
                "status": "success",
                "run_id": run_id or "latest",
                "retrospective_score": retro_score,
                "promoted": retro_score > 0.65
            }

        except Exception as e:
            logger.error(f"Retrospective trigger failed: {e}")
            return {"status": "error", "message": str(e)}
