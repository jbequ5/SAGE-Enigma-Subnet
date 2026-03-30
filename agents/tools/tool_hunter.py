# agents/tools/tool_hunter.py
# Hybrid ToolHunter with automatic HF model download + ReadyAI llms.txt (SN33) grounding

import json
import os
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

from agents.memory import memory
from agents.tools.compute import ComputeRouter
from huggingface_hub import snapshot_download

# New: ReadyAI integration
from agents.tools.readyai_tool import readyai_tool

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
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        print("🔍 ToolHunter: Hybrid mode active (registry + live search + HF auto-download + ReadyAI llms.txt)")

    def hunt_and_integrate(self, gap_description: str, subtask: str, challenge_context: str = "") -> Dict[str, Any]:
        registry = load_registry()
        query = (gap_description + " " + subtask + " " + challenge_context).lower()

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

        # Step 2: ReadyAI llms.txt grounding (great for domains, companies, topics)
        if any(word in query for word in ["company", "domain", "technology", "research", "org", "site", "arxiv", "who", "gov"]):
            readyai_result = readyai_tool.query(gap_description + " " + subtask, limit=4)
            if readyai_result.get("success"):
                memory.add(text=f"ReadyAI grounding: {readyai_result['summary']}", 
                          metadata={"source": "readyai", "query": gap_description})
                
                return {
                    "status": "success",
                    "source": "readyai_llms.txt",
                    "results": readyai_result["results"],
                    "summary": readyai_result["summary"],
                    "recommendation": "Use structured domain knowledge from ReadyAI for grounding"
                }

        # Step 3: Full live hunt (GitHub + HF)
        search_task = f"""Generate precise search queries for this SN63 gap:
Gap: {gap_description}
Subtask: {subtask}
Context: {challenge_context or 'General verifier-driven challenge'}

Reply exactly:
Queries: ["github query1", "huggingface query2"]"""
        queries_response = self.compute.run_on_compute(search_task, task_type="toolhunter")
        queries = self._extract_queries(queries_response)

        candidates = self._real_search(queries)

        decision_task = f"""Rank these candidates for SN63 gap: {gap_description}

Candidates:
{json.dumps(candidates, indent=2)}

Choose the SINGLE best HF model or tool (or 'none'). Provide:
- chosen_item (repo URL or HF model name)
- integration_idea
- confidence (0-10)

JSON only."""
        decision = self.compute.run_on_compute(decision_task, task_type="toolhunter")
        result = self._parse_json(decision)

        if result.get("chosen_item") in (None, "none") or result.get("confidence", 0) < 6:
            return self._create_skip_result(result.get("reason", "No suitable item"))

        # Auto-download if it's a Hugging Face model
        if "/" in result.get("chosen_item", "") and "github" not in result["chosen_item"].lower():
            self._auto_download_hf_model(result["chosen_item"])

        # Add to registry
        registry = load_registry()
        registry["models"].append({
            "name": result.get("chosen_item"),
            "keywords": [word.lower() for word in subtask.split() if len(word) > 3],
            "added": datetime.now().isoformat()
        })
        save_registry(registry)

        memory.add(text=f"ToolHunter recommendation: {result['chosen_item']}", 
                  metadata={"subtask": subtask, "confidence": result["confidence"]})

        return {
            "status": "success",
            "chosen_item": result.get("chosen_item"),
            "integration_idea": result.get("integration_idea", ""),
            "confidence": result.get("confidence", 5),
            "miner_action": "Model auto-downloaded and ready for next run"
        }

    def _auto_download_hf_model(self, model_id: str):
        """Automatically download high-confidence HF models."""
        try:
            target_dir = self.models_dir / model_id.replace("/", "__")
            if target_dir.exists():
                logger.info(f"Model {model_id} already cached")
                return
            print(f"📥 Auto-downloading recommended model: {model_id}")
            snapshot_download(repo_id=model_id, local_dir=target_dir, local_dir_use_symlinks=False)
            logger.info(f"✅ Successfully downloaded {model_id}")
        except Exception as e:
            logger.warning(f"Auto-download failed for {model_id}: {e}")

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
            return {"chosen_item": None, "confidence": 0}

    def _create_skip_result(self, reason: str) -> Dict:
        return {"status": "skip", "reason": reason}

# Global instance
tool_hunter = ToolHunter()
