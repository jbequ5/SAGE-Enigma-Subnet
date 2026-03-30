# agents/tools/readyai_tool.py
# ReadyAI llms.txt integration (SN33) - Domain-aware structured knowledge

import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ReadyAI_KnowledgeTool:
    def __init__(self):
        self.api_base = "https://llms-text.ai/api"
        self.cache_dir = Path("cache/readyai")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def query(self, search_term: str, limit: int = 5) -> Dict[str, Any]:
        """Query llms.txt knowledge base for any domain or topic."""
        try:
            response = requests.get(
                f"{self.api_base}/search-llms",
                params={"q": search_term, "limit": limit},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])[:limit]
            
            if results:
                logger.info(f"ReadyAI returned {len(results)} structured summaries for '{search_term}'")
                return {
                    "success": True,
                    "query": search_term,
                    "results": results,
                    "summary": f"Found structured knowledge for {len(results)} sources related to '{search_term}'"
                }
            else:
                return {"success": False, "message": f"No llms.txt data found for '{search_term}'"}

        except Exception as e:
            logger.warning(f"ReadyAI query failed: {e}")
            return {"success": False, "message": f"ReadyAI lookup error: {str(e)[:100]}"}

    def get_domain_summary(self, domain: str) -> str:
        """Get clean summary for a specific domain (e.g. 'openai.com', 'arxiv.org')."""
        result = self.query(domain, limit=3)
        if result["success"] and result["results"]:
            return "\n\n".join([r.get("summary", r.get("content", "")) for r in result["results"]])
        return f"[No structured data available for {domain}]"

    def get_structured_knowledge(self, query: str, limit: int = 4) -> Dict[str, Any]:
        """Main public method used by ToolHunter and Arbos"""
        return self.query(query, limit=limit)

# Global instance
readyai_tool = ReadyAI_KnowledgeTool()
