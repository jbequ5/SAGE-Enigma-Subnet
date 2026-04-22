import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path("operations_config.json")

def load_config() -> Dict[str, Any]:
    """Load shared wizard config. Raises if missing."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            "operations_config.json not found. Run the 0.9.10 wizard first or provide --config."
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: Dict[str, Any]) -> None:
    """Save shared config."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
