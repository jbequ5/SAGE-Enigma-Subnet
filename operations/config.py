import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path("operations_config.json")

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("operations_config.json not found. Run the wizard first.")
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config: Dict[str, Any]):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
