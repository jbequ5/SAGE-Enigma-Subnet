import os
import torch
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import time
import psutil

logger = logging.getLogger(__name__)

# agents/tools/compute.py
class ComputeRouter:
    def __init__(self):
        self.monitor = ResourceMonitor(max_hours=4.0)
        self.tool_env_manager = None

    def set_tool_env_manager(self, manager):
        self.tool_env_manager = manager

    def get_preferred_backend(self, code_snippet: str) -> str:
        """Decide best backend attempt order."""
        lower = code_snippet.lower()
        if any(k in lower for k in ["sympy", "solve", "integrate", "symbol"]):
            return "sympy"
        if any(k in lower for k in ["cirq", "quantum", "qubit", "circuit"]):
            return "cirq"
        if any(k in lower for k in ["z3", "solver", "satisfi", "constraint"]):
            return "z3"
        return "default"

    def execute(self, code: str, local_vars: Dict = None, approximation_mode: str = "auto") -> bool:
        """Router calls the single source of truth in ValidationOracle."""
        if local_vars is None:
            local_vars = {}

        # Try preferred real backend first via oracle's safe_exec
        preferred = self.get_preferred_backend(code)
        local_vars["preferred_backend"] = preferred

        # Delegate to ValidationOracle's safe_exec (the only safe place)
        if hasattr(self, 'oracle') and self.oracle:
            return self.oracle._safe_exec(code, local_vars, approximation_mode)
        else:
            # Fallback if oracle not wired yet
            logger.warning("ComputeRouter called without oracle wired — using approximation only")
            local_vars["approximation_used"] = True
            return True

# Global instance
compute_router = ComputeRouter()
