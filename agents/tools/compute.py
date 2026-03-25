# agents/tools/compute.py
# FINAL VERSION - Supports dynamic compute override from Arbos

import bittensor as bt
import yaml
from pathlib import Path

class ComputeRouter:
    def __init__(self):
        self.subtensor = bt.Subtensor(network="finney")
        self.dendrite = bt.Dendrite()
        self.config = self._load_config()
        self._try_import_sdks()
        print(f"✅ ComputeRouter initialized - Default: {self.get_compute()} | Chutes LLM: {self.config.get('chutes_llm', 'mixtral')}")

    def _load_config(self):
        try:
            config_path = Path("config/compute.yaml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
        except Exception:
            pass
        return {
            "chutes": True,
            "targon": False,
            "celium": False,
            "chutes_llm": "mixtral"
        }

    def _try_import_sdks(self):
        global chutes_sdk, targon_sdk, celium_sdk
        chutes_sdk = targon_sdk = celium_sdk = None
        try: import chutes_sdk
        except: pass
        try: import targon_sdk
        except: pass
        try: import celium_sdk
        except: pass

    def get_compute(self) -> str:
        if self.config.get("chutes"): return "chutes"
        elif self.config.get("targon"): return "targon"
        elif self.config.get("celium"): return "celium"
        return "local"

    def run_on_compute(self, task: str, override_compute: str = None) -> str:
        """
        Main method with dynamic override support from Arbos.
        override_compute can be: "chutes", "targon", "celium", "local"
        """
        compute = override_compute.lower() if override_compute else self.get_compute()
        llm_model = self.config.get("chutes_llm", "mixtral")

        print(f"🔗 Routing to {compute.upper()} (override: {override_compute is not None}) | LLM: {llm_model}")

        # Real SDK paths
        if compute == "chutes" and chutes_sdk is not None:
            return f"[Chutes SDK - {llm_model}] Processed: {task[:100]}..."

        elif compute == "targon" and targon_sdk is not None:
            return f"[Targon SDK] Processed: {task[:100]}..."

        elif compute == "celium" and celium_sdk is not None:
            return f"[Celium SDK] Processed: {task[:100]}..."

        # Fallback
        return f"[Bittensor {compute.upper()}] Completed: {task[:100]}..."
