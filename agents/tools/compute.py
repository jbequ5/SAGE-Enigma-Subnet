# agents/tools/compute.py - v2.0 MAXIMUM CAPABILITY ComputeRouter
# Fully resource-aware, model-registry integrated, verifier-first, and SOTA-gated

import os
import torch
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import time
import psutil

logger = logging.getLogger(__name__)

class ResourceMonitor:
    """High-precision resource monitoring with safe fallbacks."""
    def __init__(self, max_hours: float = 3.8):
        self.max_hours = max_hours
        self.start_time = time.time()
        self.vram_warning_threshold = 2.0  # GB

    def elapsed_hours(self) -> float:
        return (time.time() - self.start_time) / 3600.0

    def get_available_vram_gb(self) -> float:
        try:
            if torch.cuda.is_available():
                return torch.cuda.get_device_properties(0).total_memory / (1024 ** 3) - torch.cuda.memory_allocated() / (1024 ** 3)
            return 999.0  # CPU mode
        except:
            return 8.0

    def get_cpu_percent(self) -> float:
        return psutil.cpu_percent(interval=0.1)

    def get_memory_percent(self) -> float:
        return psutil.virtual_memory().percent

    def is_safe(self) -> bool:
        """SOTA safety gate for compute-intensive operations."""
        if self.elapsed_hours() > self.max_hours * 0.92:
            return False
        if self.get_available_vram_gb() < self.vram_warning_threshold:
            return False
        if self.get_memory_percent() > 92:
            return False
        return True


class ComputeRouter:
    """Central compute router — model registry aware, resource-gated, verifier-first."""

    def __init__(self):
        self.current_mode = "local_gpu"
        self.monitor = ResourceMonitor(max_hours=3.8)
        self.model_registry = None  # wired from ArbosManager

    def set_mode(self, mode: str = "local_gpu"):
        self.current_mode = mode
        logger.info(f"ComputeRouter mode set to: {mode}")

    def get_optimal_model(self, role: str = "default", subtask: str = None) -> Dict:
        """Return best model config based on role, resources, and registry."""
        if self.model_registry is None:
            # Fallback safe defaults
            return {
                "model_name": "carnice-9b" if self.current_mode == "local_gpu" else "deepseek-r1",
                "endpoint": "local_ollama" if self.current_mode == "local_gpu" else "api",
                "max_tokens": 1400,
                "temperature": 0.35
            }

        # Real registry routing
        rules = self.model_registry.get("routing_rules", {})
        models = self.model_registry.get("models", {})

        if role == "planner" or "planning" in (subtask or "").lower():
            return models.get(rules.get("planner_model", "DeepSeek-R1-Distill-Qwen-14B"), models.get("default"))

        # Resource-aware fallback
        if self.monitor.get_available_vram_gb() < 8.0:
            return models.get("Carnice-9B-Q4_K_M", models.get("default"))

        return models.get(rules.get("default", "Carnice-9B-Q4_K_M"))

    def call(self, prompt: str, temperature: float = 0.35, max_tokens: int = 1400, 
             role: str = "default", subtask: str = None, **kwargs) -> str:
        """Main entry point — resource-gated, model-routed LLM call."""
        if not self.monitor.is_safe():
            logger.warning("ComputeRouter safety gate triggered — reducing load")
            max_tokens = min(max_tokens, 800)
            temperature = min(temperature, 0.25)

        model_config = self.get_optimal_model(role=role, subtask=subtask)

        logger.debug(f"ComputeRouter calling {model_config.get('model_name')} | role={role} | tokens={max_tokens}")

        # This is where you wire your actual harness/ollama/anthropic call
        # For now, placeholder — replace with your real harness
        try:
            # Example: self.harness.call_llm(...)
            response = f"[SIMULATED RESPONSE FROM {model_config.get('model_name')}] {prompt[-200:]}..."
            return response
        except Exception as e:
            logger.error(f"ComputeRouter call failed: {e}")
            return "[ComputeRouter fallback — LLM call failed]"

    def set_model_registry(self, registry: Dict):
        """Wire from ArbosManager"""
        self.model_registry = registry
        logger.info("ComputeRouter wired to full model registry")


# Global instance
compute_router = ComputeRouter()
