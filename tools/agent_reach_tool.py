import requests
from bs4 import BeautifulSoup
import hashlib
from pathlib import Path
import logging
from cachetools import TTLCache
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AgentReachTool:
    """SOTA AgentReachTool — web content fetching with memory + disk cache, BeautifulSoup cleaning, SOTA gating, and high-signal routing."""

    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 200):
        self.cache = TTLCache(maxsize=max_cache_size, ttl=cache_ttl)
        self.cache_dir = Path(".cache/agent_reach")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Enigma-Machine-Miner-AgentReach/2.1'})
        self.arbos = None
        self.validator = None
        self.intelligence = None
        logger.info("✅ AgentReachTool v0.9.13+ SOTA initialized — memory + disk cache + full SOTA gating")

    def set_arbos(self, arbos):
        self.arbos = arbos
        if arbos:
            self.validator = getattr(arbos, 'validator', None)
            self.intelligence = getattr(arbos, 'intelligence', None)

    def _get_cache_key(self, url: str) -> str:
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _load_disk_cache(self, key: str) -> Optional[str]:
        file = self.cache_dir / f"{key}.txt"
        if file.exists():
            try:
                return file.read_text(encoding="utf-8")
            except Exception:
                pass
        return None

    def _save_disk_cache(self, key: str, content: str):
        file = self.cache_dir / f"{key}.txt"
        try:
            file.write_text(content, encoding="utf-8")
        except Exception:
            pass

    def fetch_url_content(self, url: str, max_length: int = 12000, timeout: int = 15) -> str:
        if not url or not url.startswith(("http://", "https://")):
            return "Invalid URL provided."

        key = self._get_cache_key(url)

        # Memory cache
        if key in self.cache:
            return self.cache[key]

        # Disk cache
        cached = self._load_disk_cache(key)
        if cached:
            self.cache[key] = cached
            return cached

        # Live fetch
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            # Clean unwanted tags
            for tag in soup(["script", "style", "nav", "header", "footer", "aside", "svg", "img"]):
                tag.decompose()

            text = soup.get_text(separator="\n", strip=True)
            lines = (line.strip() for line in text.splitlines())
            clean_text = "\n".join(line for line in lines if line)

            if len(clean_text) > max_length:
                clean_text = clean_text[:max_length] + "\n... [truncated]"

            # SOTA gating (7D / verifier integration)
            if self.arbos and self.validator and hasattr(self.validator, '_compute_verifier_quality'):
                try:
                    gate = self.validator._compute_verifier_quality(clean_text, [])
                    if gate.get("verifier_quality", 0) < 0.65:
                        clean_text += "\n[Agent-Reach: Content failed SOTA gate — low signal]"
                except Exception:
                    pass  # safe fallback

            # Cache the result
            self.cache[key] = clean_text
            self._save_disk_cache(key, clean_text)

            # High-signal routing
            if len(clean_text) > 800 and self.intelligence and hasattr(self.intelligence, 'route_to_vaults'):
                run_data = {
                    "insight_score": 0.85,
                    "key_takeaway": f"Agent-Reach fetched high-signal content from {url}",
                    "predictive_power": getattr(self.arbos, 'predictive_power', 0.0) if self.arbos else 0.0,
                    "flywheel_step": "agent_reach_to_vaults"
                }
                self.intelligence.route_to_vaults(run_data)

            return clean_text

        except Exception:
            fallback = f"[Agent-Reach fallback] Could not retrieve {url}."
            self.cache[key] = fallback
            self._save_disk_cache(key, fallback)
            return fallback

    def get_content_with_score(self, url: str) -> Dict[str, Any]:
        """Helper: returns content + basic EFS/SOTA hint for retrospective/audit flows."""
        content = self.fetch_url_content(url)
        return {
            "url": url,
            "content": content,
            "length": len(content),
            "timestamp": datetime.now().isoformat(),
            "sota_hint": "high_signal" if len(content) > 800 else "low_signal",
            "verifier_quality_hint": getattr(self.validator, 'last_verifier_quality', 0.0) if self.validator else 0.0
        }

# Global instance
agent_reach_tool = AgentReachTool()
