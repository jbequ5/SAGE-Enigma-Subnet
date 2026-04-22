import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

TELEMETRY_PATH = Path("operations_telemetry.jsonl")

def log_telemetry(entry: Dict[str, Any]):
    """Log operations telemetry to JSONL for Synapse."""
    entry["timestamp"] = datetime.utcnow().isoformat()
    with open(TELEMETRY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
