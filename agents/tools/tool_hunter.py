# agents/tools/tool_hunter.py
# Hybrid ToolHunter: Registry first (fast) → Full live hunt when needed

import json
import os
import subprocess
import tempfile
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.memory import memory
from agents.tools.compute import ComputeRouter
from agents.tools.resource_aware import ResourceMonitor

REGISTRY_PATH = "agents/tools/registry.json"

def load_registry():
    if os.path.exists(REGISTRY_PATH):
        try:
            with open(REGISTRY_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tools": [], "models": [], "last_updated": ""}

def save_registry(registry):
    registry["last_updated"] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

class ToolHunter:
    def __init__(self):
        self.compute = ComputeRouter()
        self.temp_dir = Path(tempfile.gettempdir()) / "toolhunter_cache"
        self.temp_dir.mkdir(exist_ok=True)
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        print("🔍 ToolHunter: Hybrid mode active (registry + live search)")

    def hunt_and_integrate(self, gap_description: str, subtask: str, challenge_context: str = "") -> Dict[str, Any]:
        registry = load_registry()
        query = (gap_description + " " + subtask).lower()

        # Step 1: Fast registry lookup
        for tool in registry.get("tools", []):
            keywords = [k.lower() for k in tool.get("keywords", [])]
            if any(k in query for k in keywords):
                return {
                    "status": "success",
                    "tool_name": tool.get("name"),
                    "recommendation": tool.get("install_cmd", ""),
                    "source": "registry"
                }

        for model in registry.get("models", []):
            keywords = [k.lower() for k in model.get("keywords", [])]
            if any(k in query for k in keywords):
                return {
                    "status": "success",
                    "model_name": model.get("name"),
                    "compatibility": model.get("compatibility", ""),
                    "recommendation": model.get("install_cmd", ""),
                    "source": "registry"
                }

        # Step 2: Full live hunt if registry match is weak
        monitor = ResourceMonitor(max_hours=0.5)

        search_task = f"""Generate precise search queries for this SN63 gap:
Gap: {gap_description}
Subtask: {subtask}
Context: {challenge_context or 'Quantum Rings simulator, stabilizer preprocessing, circuit optimization'}

Reply exactly:
Queries: ["github query1", "arxiv query2"]"""
        queries_response = self.compute.run_on_compute(search_task)
        queries = self._extract_queries(queries_response)

        candidates = self._real_search(queries)

        decision_task = f"""Rank these candidates for SN63 gap: {gap_description}

Candidates:
{json.dumps(candidates, indent=2)}

Choose the SINGLE best (or 'none'). Provide:
- chosen_tool (repo URL or package)
- integration_code (wrapper snippet for Quantum Rings)
- patch (adapter diff or description)
- confidence (0-10)

JSON only."""
        decision = self.compute.run_on_compute(decision_task)
        result = self._parse_json(decision)

        if result.get("chosen_tool") in (None, "none") or result.get("confidence", 0) < 5:
            return self._create_skip_result(result.get("reason", "No suitable tool"))

        integration_attempt = self._attempt_safe_install_and_test(result, gap_description, subtask)

        if integration_attempt["success"]:
            # Auto-add successful live result to registry
            registry = load_registry()
            registry["tools"].append({
                "name": result.get("chosen_tool"),
                "keywords": [word.lower() for word in subtask.split() if len(word) > 3],
                "install_cmd": f"git clone {result.get('chosen_tool')}",
                "added": datetime.now().isoformat()
            })
            save_registry(registry)

            memory.add(text=f"ToolHunter success: {result['chosen_tool']}", metadata={"subtask": subtask, "confidence": result["confidence"]})
            return {"status": "success", **result, "test_result": integration_attempt["test_output"], "miner_action": None}

        recommendation = self._generate_miner_recommendation(result, integration_attempt, gap_description, subtask)
        return {
            "status": "manual_required",
            "tool_name": result.get("chosen_tool"),
            "integration_code": result.get("integration_code"),
            "patch": result.get("patch"),
            "failure_reason": integration_attempt["test_output"],
            "miner_recommendation": recommendation,
            "confidence": result.get("confidence", 5)
        }

    def _real_search(self, queries: List[str]) -> List[Dict]:
        candidates = []
        for q in queries[:2]:
            try:
                url = f"https://api.github.com/search/repositories?q={q.replace(' ', '+')}&sort=stars&order=desc&per_page=3"
                headers = {"Authorization": f"token {self.github_token}"} if self.github_token else {}
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    for item in r.json().get("items", [])[:2]:
                        candidates.append({
                            "source": "github",
                            "name": item["full_name"],
                            "url": item["html_url"],
                            "stars": item["stargazers_count"],
                            "description": item.get("description", "")
                        })
            except Exception:
                pass

            try:
                arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{q.replace(' ', '+')}&max_results=3"
                r = requests.get(arxiv_url, timeout=10)
                if r.status_code == 200 and "<entry>" in r.text:
                    candidates.append({"source": "arxiv", "name": q, "url": f"https://arxiv.org/search/?query={q}", "description": "arXiv paper - likely has code"})
            except Exception:
                pass
        return candidates[:5]

    def _attempt_safe_install_and_test(self, decision: Dict, gap: str, subtask: str) -> Dict[str, Any]:
        tool_url = decision.get("chosen_tool", "")
        if not tool_url or "github.com" not in tool_url:
            return {"success": False, "test_output": "Non-GitHub tool - manual only"}

        try:
            temp_env = self.temp_dir / f"tool_{int(time.time())}"
            temp_env.mkdir(exist_ok=True)

            subprocess.run(["git", "clone", tool_url, temp_env], check=True, timeout=60, cwd=temp_env.parent)

            test_code = f"""
import sys
sys.path.insert(0, '{temp_env}')
try:
    import {tool_url.split('/')[-1].replace('-', '_')}
    print('Import successful')
    print('Quantum Rings adapter ready for manual hook')
except Exception as e:
    print(f'Import failed: {{e}}')
"""
            with open(temp_env / "test_tool.py", "w") as f:
                f.write(test_code)

            result = subprocess.run(["python", str(temp_env / "test_tool.py")], capture_output=True, text=True, timeout=30, cwd=temp_env)
            return {"success": result.returncode == 0, "test_output": result.stdout + result.stderr}
        except Exception as e:
            return {"success": False, "test_output": f"Clone/test failed: {str(e)}"}

    def _generate_miner_recommendation(self, decision: Dict, attempt: Dict, gap: str, subtask: str) -> str:
        tool = decision.get("chosen_tool", "Unknown")
        return f"""🔧 TOOLHUNTER MANUAL ESCALATION

Gap: {gap}
Subtask: {subtask}
Promising Tool: {tool}

Automated attempt failed: {attempt.get('test_output', 'Unknown')[:400]}

Manual Steps:
1. git clone {tool}
2. cd <repo>
3. pip install -e . --no-deps
4. Test import

Add this wrapper:
{decision.get('integration_code', '# Paste suggested wrapper here')}"""

    def _extract_queries(self, response: str) -> List[str]:
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            return json.loads(response[start:end])
        except:
            return [response.strip()[:100]]

    def _parse_json(self, raw: str) -> Dict:
        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except:
            return {"chosen_tool": None, "confidence": 0}

    def _create_skip_result(self, reason: str) -> Dict:
        return {"status": "skip", "reason": reason}

tool_hunter = ToolHunter()
