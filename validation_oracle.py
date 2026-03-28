import subprocess
import json
from pathlib import Path
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class ValidationOracle:
    def __init__(self, validator_path: str = "./validator.py"):
        self.validator_path = Path(validator_path).resolve()
        if not self.validator_path.exists():
            logger.error(f"Validator not found: {self.validator_path}")
            raise FileNotFoundError(str(self.validator_path))
        logger.info(f"✅ ValidationOracle initialized with: {self.validator_path}")

        # Store last run results for easy access in packaging
        self.last_score = 0.0
        self.last_fidelity = 0.0
        self.last_vvd_ready = False
        self.last_notes = ""

    def run(self, candidate_solution: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
        """Run official SN63 miner validation code and return structured metrics."""
        try:
            input_json = json.dumps(candidate_solution)
            result = subprocess.run(
                [str(self.validator_path), "--input", input_json],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning(f"Validator failed (code {result.returncode}): {result.stderr[:500]}")
                error_result = {"validation_score": 0.0, "passed": False, "error": result.stderr.strip()}
                self._update_last_results(error_result)
                return error_result

            metrics = json.loads(result.stdout)
            result_dict = {
                "validation_score": float(metrics.get("overall_score", 0.0)),
                "fidelity": float(metrics.get("fidelity", 0.0)),
                "passed": bool(metrics.get("valid", False)),
                "vvd_ready": bool(metrics.get("vvd_ready", False)),
                "notes": metrics.get("details", ""),
                "raw_output": metrics
            }
            self._update_last_results(result_dict)
            return result_dict

        except json.JSONDecodeError:
            logger.error("Validator returned invalid JSON")
            error_result = {"validation_score": 0.0, "passed": False, "error": "Invalid JSON output"}
            self._update_last_results(error_result)
            return error_result
        except subprocess.TimeoutExpired:
            logger.error("Validator timed out")
            error_result = {"validation_score": 0.0, "passed": False, "error": "Timeout"}
            self._update_last_results(error_result)
            return error_result
        except Exception as e:
            logger.exception("Validator error")
            error_result = {"validation_score": 0.0, "passed": False, "error": str(e)}
            self._update_last_results(error_result)
            return error_result

    def _update_last_results(self, result: Dict):
        self.last_score = result.get("validation_score", 0.0)
        self.last_fidelity = result.get("fidelity", 0.0)
        self.last_vvd_ready = result.get("vvd_ready", False)
        self.last_notes = result.get("notes", "")
