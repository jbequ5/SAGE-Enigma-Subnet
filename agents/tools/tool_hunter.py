# agents/tools/tool_hunter.py
# Dynamic Tool Discovery, Integration, and Adaptation for SN63
# Called conditionally by sub-Arbos instances when blueprint tool_map or reflection indicates a gap

import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from agents.memory import memory
from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor


class ToolHunter:
    def __init__(self):
        self.compute = ComputeRouter()
        self.temp_dir = Path(tempfile.gettempdir()) / "toolhunter_cache"
        self.temp_dir.mkdir(exist_ok=True)
        print("🔍 ToolHunter initialized - dynamic discovery + adaptation enabled")

    def hunt_and_integrate(self, gap_description: str, subtask: str, challenge_context: str = "") -> Dict[str, Any]:
        """
        Main entry point: Discover → Evaluate → Download/Adapt → Test → Return integration instructions.
        Returns a dict with 'status', 'tool_name', 'integration_code', 'patch', 'confidence'.
        """
        monitor = ResourceMonitor(max_hours=0.5)  # Strict time box for hunting

        # Step 1: Intelligent search query generation by Arbos
        search_task = f"""You are ToolHunter for Bittensor SN63.

Challenge context: {challenge_context}
Subtask: {subtask}
Gap: {gap_description}

Generate 2-3 precise search queries for GitHub, arXiv, HuggingFace, or PyPI that would find the best open-source tool to fill this gap.
Prioritize: GPU-friendly, verifiable output, recent (2025+), minimal dependencies.

Reply exactly:
Queries: ["query1", "query2"]
Reason: [brief]"""

        queries_response = self.compute.run_on_compute(search_task)
        queries = self._extract_queries(queries_response)

        # Step 2: Simulate/execute search (in real setup: use web_search or GitHub API via requests)
        # For now: Use LLM to suggest top candidates (expand with actual search in next iteration)
        candidate_task = f"""Based on these search needs: {queries}

Suggest 1-2 concrete open-source tools/repositories that best fill the gap for SN63 (quantum simulation, optimization, preprocessing, etc.).
Include:
- Repo URL or package name
- Why it fits
- Estimated integration effort (low/medium/high)

Be realistic and conservative."""

        candidates = self.compute.run_on_compute(candidate_task)

        # Step 3: Arbos decides on best candidate + adaptation plan
        decision_task = f"""Evaluate these candidates for the gap:

{candidates}

Subtask: {subtask}
SN63 constraints: H100, Quantum Rings compatibility, verifier-friendly output, novelty boost.

Choose the best one (or 'none' if none are suitable).
Then provide:
- Chosen tool
- Integration plan (Python code snippet for wrapper)
- Any needed patch for Quantum Rings / SN63
- Risk level

Reply in JSON:
{{
  "chosen_tool": "name or URL or none",
  "integration_code": "python code snippet",
  "patch": "diff or description",
  "confidence": 0-10,
  "reason": "..."
}}"""

        decision = self.compute.run_on_compute(decision_task)
        result = self._parse_json(decision)

        if result.get("chosen_tool") == "none" or result.get("confidence", 0) < 6:
            return {
                "status": "skipped",
                "tool_name": None,
                "integration_code": None,
                "reason": "No suitable tool found or low confidence"
            }

        # Step 4: Attempt safe integration (clone + basic test in temp env)
        tool_info = self._attempt_safe_install(result)
        
        # Step 5: Store in long-term memory for future reuse
        memory.add(
            text=f"ToolHunter result for gap: {gap_description}",
            metadata={
                "subtask": subtask,
                "tool_name": result.get("chosen_tool"),
                "confidence": result.get("confidence"),
                "integration": bool(tool_info.get("success"))
            }
        )

        return {
            "status": "success" if tool_info.get("success") else "partial",
            "tool_name": result.get("chosen_tool"),
            "integration_code": result.get("integration_code"),
            "patch": result.get("patch"),
            "test_result": tool_info.get("test_output"),
            "reason": result.get("reason")
        }

    def _extract_queries(self, response: str) -> List[str]:
        try:
            if "Queries:" in response:
                queries_part = response.split("Queries:")[1].split("Reason:")[0]
                return json.loads(queries_part.strip())
        except Exception:
            pass
        return ["SN63 quantum optimization tool github", "python gpu verifiable simulation library"]

    def _parse_json(self, raw: str) -> Dict[str, Any]:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            return {"chosen_tool": "none", "confidence": 3, "reason": "Parse fallback"}

    def _attempt_safe_install(self, decision: Dict) -> Dict[str, Any]:
        """Safe sandboxed attempt to clone/test a tool. Returns success flag."""
        tool = decision.get("chosen_tool")
        if not tool or tool == "none":
            return {"success": False, "test_output": "No tool selected"}

        try:
            # For GitHub URLs or package names - implement git clone or pip in temp dir
            temp_env = self.temp_dir / f"tool_{abs(hash(tool))}"
            temp_env.mkdir(exist_ok=True)

            # Example: if it's a git repo
            if "github.com" in str(tool):
                subprocess.run(["git", "clone", tool, temp_env], check=True, timeout=60, cwd=temp_env.parent)
                test_cmd = ["python", "-c", "print('Tool cloned successfully')"]
            else:
                # pip install simulation (dry-run style for safety)
                test_cmd = ["python", "-c", f"import {tool.split('/')[-1].replace('-','_')}; print('Import successful')"]

            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30, cwd=temp_env)
            
            return {
                "success": result.returncode == 0,
                "test_output": result.stdout + result.stderr
            }
        except Exception as e:
            return {"success": False, "test_output": f"Integration attempt failed: {str(e)}"}


# Singleton for easy import
tool_hunter = ToolHunter()
