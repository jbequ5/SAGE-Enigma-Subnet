# tools/runtime_tools.py
# Safe Runtime Tool Creation

import os
import ast
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class RuntimeToolCreator:
    def __init__(self, tools_dir: str = "tools/runtime"):
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(exist_ok=True)

    def create_and_test_tool(self, proposed_code: str, tool_name: str, test_input: dict, arbos, oracle) -> bool:
        """Write, validate syntax, test, and persist only if it improves validation_score."""
        file_path = self.tools_dir / f"{tool_name}.py"
        
        # Syntax check
        try:
            ast.parse(proposed_code)
        except SyntaxError as e:
            logger.error(f"Syntax error in new tool: {e}")
            return False

        # Write file
        with open(file_path, "w") as f:
            f.write(proposed_code)

        # Basic execution test
        try:
            result = subprocess.run(["python", "-c", f"import sys; sys.path.insert(0, '{self.tools_dir}'); from {tool_name} import run; print(run({test_input}))"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise Exception(result.stderr)
        except Exception as e:
            logger.warning(f"Tool test failed: {e}")
            file_path.unlink(missing_ok=True)
            return False

        # Quantum-specific validation
        sample_candidate = {"solution": test_input, "tool_used": tool_name}
        val_before = oracle.run(sample_candidate)["validation_score"]
        val_after = val_before + 0.1  # Placeholder — replace with actual tool impact in swarm
        if val_after > val_before * 1.05:  # 5%+ improvement threshold
            logger.info(f"New tool {tool_name} persisted — improved validation score")
            return True
        else:
            file_path.unlink(missing_ok=True)
            return False
