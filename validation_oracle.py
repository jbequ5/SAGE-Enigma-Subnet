import subprocess
import json
from pathlib import Path
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class ValidationOracle:
    def __init__(self, validator_path: str):
        self.validator_path = Path(validator_path).resolve()
        if not self.validator_path.exists():
            logger.error(f"Validator not found: {self.validator_path}")
            raise FileNotFoundError(str(self.validator_path))
        logger.info(f"ValidationOracle initialized with: {self.validator_path}")

    def run(self, candidate_solution: Dict[str, Any], timeout: int = 300) -> Dict[str, Any]:
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
                return {"validation_score": 0.0, "passed": False, "error": result.stderr.strip()}

            metrics = json.loads(result.stdout)
            return {
                "validation_score": float(metrics.get("overall_score", 0.0)),
                "fidelity": float(metrics.get("fidelity", 0.0)),
                "passed": bool(metrics.get("valid", False)),
                "vvd_ready": bool(metrics.get("vvd_ready", False)),
                "notes": metrics.get("details", ""),
                "raw_output": metrics
            }
        except json.JSONDecodeError:
            logger.error("Validator returned invalid JSON")
            return {"validation_score": 0.0, "passed": False, "error": "Invalid JSON output"}
        except subprocess.TimeoutExpired:
            logger.error("Validator timed out")
            return {"validation_score": 0.0, "passed": False, "error": "Timeout"}
        except Exception as e:
            logger.exception("Validator error")
            return {"validation_score": 0.0, "passed": False, "error": str(e)}
