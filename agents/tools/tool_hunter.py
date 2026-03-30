# agents/tools/tool_hunter.py
# Hybrid ToolHunter: Registry first (fast) → Full live hunt when needed
# Hardened version: Suggestions only — no runtime installation or execution

import json
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.memory import memory
from agents.tools.compute import ComputeRouter

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
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        print("🔍 ToolHunter: Hybrid mode active (registry + live search) — Suggestions only")

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

        # Step 2: Full live hunt if registry match is weak (suggestions only)
        search_task = f"""Generate precise search queries for this SN63 gap:
Gap: {gap_description}
Subtask: {subtask}
Context: {challenge_context or 'General verifier-driven challenge'}

Reply exactly:
Queries: ["github query1", "arxiv query2"]"""
        queries_response = self.compute.run_on_compute(search_task, task_type="toolhunter")
        queries = self._extract_queries(queries_response)

        candidates = self._real_search(queries)

        decision_task = f"""Rank these candidates for SN63 gap: {gap_description}

Candidates:
{json.dumps(candidates, indent=2)}

Choose the SINGLE best (or 'none'). Provide:
- chosen_tool (repo URL or package name)
- integration_idea (how it could help)
- confidence (0-10)

JSON only."""
        decision = self.compute.run_on_compute(decision_task, task_type="toolhunter")
        result = self._parse_json(decision)

        if result.get("chosen_tool") in (None, "none") or result.get("confidence", 0) < 5:
            return self._create_skip_result(result.get("reason", "No suitable tool"))

        # Add to registry for future use (suggestion only)
        registry = load_registry()
        registry["tools"].append({
            "name": result.get("chosen_tool"),
            "keywords": [word.lower() for word in subtask.split() if len(word) > 3],
            "install_cmd": f"Manual: git clone {result.get('chosen_tool')}",
            "added": datetime.now().isoformat()
        })
        save_registry(registry)

        memory.add(text=f"ToolHunter suggestion: {result['chosen_tool']}", metadata={"subtask": subtask, "confidence": result["confidence"]})

        return {
            "status": "success",
            "tool_name": result.get("chosen_tool"),
            "integration_idea": result.get("integration_idea", ""),
            "confidence": result.get("confidence", 5),
            "miner_action": "Manual install recommended for next run"
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
        return candidates[:5]

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

# Global instance
tool_hunter = ToolHunter()
