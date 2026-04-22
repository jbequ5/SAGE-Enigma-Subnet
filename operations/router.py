from typing import Dict, List
import math

class SmartLLMRouter:
    """SOTA LLM router with automatic downscaling as swarm size grows."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_registry = config.get("model_registry", {})
        self.task_type_models = config.get("task_type_models", {})
        self.downscale_factor = config.get("downscale_factor", 0.08)

    def recommend_model(self, task_type: str, current_n: int, available_vram_gb: float) -> str:
        """Recommend best model for task type and current swarm size."""
        candidates = self.task_type_models.get(task_type, ["claude-3.5-sonnet"])
        if not candidates:
            return "claude-3.5-sonnet"

        # Downscale as N grows
        downscale = max(0.3, 1.0 - self.downscale_factor * (current_n - 1))

        # Select smaller model as swarm grows
        idx = max(0, min(len(candidates) - 1, int((1 - downscale) * len(candidates))))
        recommended = candidates[idx]

        # Safety check against available VRAM
        required_vram = self.get_model_vram_requirement(recommended)
        if required_vram > available_vram_gb * 0.8:
            # Fall back to smallest model
            return candidates[-1]

        return recommended

    def get_model_vram_requirement(self, model_name: str) -> float:
        """Return estimated VRAM requirement for the model."""
        return self.model_registry.get(model_name, {}).get("vram_gb", 24.0)
