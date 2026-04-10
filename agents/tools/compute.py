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

    def get_preferred_backend(self, code: str) -> str:
        """SOTA backend routing with PuLP support."""
        lower = code.lower()
        if any(k in lower for k in ["pulp", "lp", "milp", "linearprogram", "optimize", "maximize", "minimize", "constraint", "objective"]):
            return "pulp"
        if any(k in lower for k in ["sympy", "solve", "integrate", "symbol"]):
            return "sympy"
        if any(k in lower for k in ["cirq", "quantum", "qubit", "circuit"]):
            return "cirq"
        if any(k in lower for k in ["z3", "smt", "solver", "satisfi"]):
            return "z3"
        return "default"

    def execute(self, code: str, local_vars: Dict = None, approximation_mode: str = "auto") -> bool:
        if local_vars is None:
            local_vars = {}

        preferred = self.get_preferred_backend(code)
        local_vars["preferred_backend"] = preferred

        if preferred == "pulp":
            try:
                import pulp
                exec(code, {"pulp": pulp, "__builtins__": {}}, local_vars)
                local_vars["backend_used"] = "pulp"
                local_vars["approximation_used"] = False
                return True
            except Exception as e:
                logger.debug(f"PuLP backend failed: {e}")

        # Delegate to ValidationOracle's safe_exec for all other cases
        if self.oracle:
            return self.oracle._safe_exec(code, local_vars, approximation_mode)
        
        local_vars["approximation_used"] = True
        return True
        
# Global instance
compute_router = ComputeRouter()
