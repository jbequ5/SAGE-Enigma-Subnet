import subprocess
import venv
import json
import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict, Optional

from agents.tools.resource_aware import resource_monitor

logger = logging.getLogger(__name__)

class ToolEnvManager:
    """SOTA ToolEnvManager — safe ephemeral/persistent venvs with dynamic registration and full integration with ComputeRouter / ResourceMonitor."""

    def __init__(self):
        self.base_path = Path("~/.enigma_tools").expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
       
        self.envs_dir = Path("tools/envs")
        self.envs_dir.mkdir(parents=True, exist_ok=True)
       
        self.registry_path = Path("tools/env_registry.json")
        self.registry = self._load_registry()
       
        logger.info("✅ ToolEnvManager v0.9.13+ SOTA initialized — persistent/ephemeral venvs with dynamic registration")

    def _load_registry(self) -> Dict:
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Failed to load env registry (safe): {e}")
        return {}

    def _save_registry(self):
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")

    def create_or_get_env(self, tool_name: str, persistent: bool = True,
                         requirements: List[str] = None, install_cmd: str = None) -> Dict[str, Any]:
        """Create or reuse a virtual environment for a tool."""
        key = f"{tool_name}_{'persistent' if persistent else 'ephemeral'}"
       
        # Reuse if exists and still valid
        if key in self.registry:
            python_exe = Path(self.registry[key])
            if python_exe.exists():
                logger.debug(f"Reusing existing environment for {tool_name}")
                return {
                    "status": "success", 
                    "python_exe": str(python_exe), 
                    "reused": True,
                    "env_type": "persistent" if persistent else "ephemeral"
                }

        # Create new environment
        env_path = self.envs_dir / key
        logger.info(f"Creating new {'persistent' if persistent else 'ephemeral'} environment for {tool_name}")
        
        try:
            venv.create(env_path, with_pip=True, clear=True)
            python_exe = env_path / ("bin/python" if os.name != "nt" else "Scripts/python.exe")

            # Install requirements
            if requirements:
                pip_cmd = [str(python_exe), "-m", "pip", "install", "--upgrade"] + requirements
                subprocess.run(pip_cmd, check=True, capture_output=True, text=True)
                logger.info(f"Installed requirements for {tool_name}: {requirements}")

            # Run custom install command if provided
            if install_cmd and install_cmd.strip():
                install_cmd_list = install_cmd.strip().split()
                if install_cmd_list[0] == "pip":
                    install_cmd_list = [str(python_exe), "-m"] + install_cmd_list
                else:
                    install_cmd_list = [str(python_exe), "-m", "pip", "install"] + install_cmd_list
                subprocess.run(install_cmd_list, check=True, capture_output=True, text=True)
                logger.info(f"Ran custom install command for {tool_name}")

            # Register
            self.registry[key] = str(python_exe)
            self._save_registry()

            return {
                "status": "success",
                "python_exe": str(python_exe),
                "reused": False,
                "env_path": str(env_path),
                "env_type": "persistent" if persistent else "ephemeral"
            }

        except Exception as e:
            logger.error(f"Failed to create environment for {tool_name}: {e}")
            return {"status": "error", "error": str(e), "tool_name": tool_name}

    def get_env_python(self, tool_name: str, persistent: bool = True) -> Optional[str]:
        """Convenience method: return python executable path or None on failure."""
        result = self.create_or_get_env(tool_name, persistent=persistent)
        return result.get("python_exe") if result.get("status") == "success" else None

    def cleanup_ephemeral(self, days_old: int = 2):
        """Clean old ephemeral environments — tied to ResourceMonitor time awareness."""
        for p in self.envs_dir.glob("*_ephemeral"):
            if p.is_dir():
                try:
                    age_days = (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days
                    if age_days > days_old or resource_monitor.elapsed_hours() > resource_monitor.max_hours * 0.9:
                        shutil.rmtree(p, ignore_errors=True)
                        logger.info(f"Cleaned old ephemeral env: {p}")
                except Exception as e:
                    logger.debug(f"Failed to clean {p}: {e}")

    def list_environments(self) -> Dict[str, Any]:
        """Return summary of all registered environments for UI/Streamlit."""
        persistent = []
        ephemeral = []
        for key, path in self.registry.items():
            if "_persistent" in key:
                persistent.append({"tool": key.replace("_persistent", ""), "path": path})
            else:
                ephemeral.append({"tool": key.replace("_ephemeral", ""), "path": path})
        return {
            "persistent_count": len(persistent),
            "ephemeral_count": len(ephemeral),
            "persistent": persistent,
            "ephemeral": ephemeral,
            "total": len(self.registry)
        }

# Global instance
tool_env_manager = ToolEnvManager()
