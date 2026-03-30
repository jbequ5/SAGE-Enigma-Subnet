# agents/tools/compute.py
# Optimized Intelligent Routing with automatic Quasar download

import os
import requests
import time
from typing import Any, Dict
import logging
from huggingface_hub import snapshot_download

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        self.model_preferences = {
            "planning": "best",
            "orchestration": "best",
            "adaptation": "best",
            "re_adapt": "best",
            "subtask": "fast",
            "synthesis": "fast",
            "verification": "fast",
            "toolhunter": "fast",
            "tool_proposal": "fast",
        }

    def choose_model(self, task_type: str, novelty_level: str = "medium") -> str:
        if task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            return "best"
        return self.model_preferences.get(task_type, "fast")


class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False
        self.llm_router = LLMRouter()
        self.max_retries = 3
        self.quasar_enabled = True
        self.quasar_llm = None
        self.quasar_model_id = "silx-ai/Quasar-10B"
        self.quasar_cache_dir = Path("models/Quasar-10B")

        # Lazy-loaded frontier clients
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None

    def set_compute_source(self, source: str, endpoint: str = None):
        self.compute_source = source
        self.custom_endpoint = endpoint
        self.use_local = (source == "local")

    def enable_quasar(self, enabled: bool = True):
        self.quasar_enabled = enabled
        logger.info(f"Quasar Attention routing {'ENABLED' if enabled else 'DISABLED'}")

    def _ensure_quasar_downloaded(self):
        """Auto-download Quasar on first use if not present."""
        if self.quasar_cache_dir.exists() and any(self.quasar_cache_dir.iterdir()):
            return True
        
        logger.info(f"📥 Auto-downloading Quasar model: {self.quasar_model_id}")
        try:
            snapshot_download(
                repo_id=self.quasar_model_id,
                local_dir=str(self.quasar_cache_dir),
                local_dir_use_symlinks=False
            )
            logger.info("✅ Quasar model successfully downloaded and cached")
            return True
        except Exception as e:
            logger.error(f"Quasar download failed: {e}")
            return False

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium") -> str:
        preferred = self.llm_router.choose_model(task_type, novelty_level)

        # 1. Quasar for high-value tasks
        if self.quasar_enabled and task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            if self._ensure_quasar_downloaded():
                try:
                    if self.quasar_llm is None:
                        from vllm import LLM, SamplingParams
                        self.quasar_llm = LLM(
                            model=str(self.quasar_cache_dir),
                            trust_remote_code=True,
                            gpu_memory_utilization=0.85
                        )
                    sampling = SamplingParams(temperature=temperature, max_tokens=4096)
                    outputs = self.quasar_llm.generate(task, sampling)
                    logger.info(f"Used Quasar for {task_type}")
                    return outputs[0].outputs[0].text.strip()
                except Exception as e:
                    logger.warning(f"Quasar inference failed: {e}")

        # 2. Local vLLM fallback
        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    logger.info(f"Used local vLLM for {task_type}")
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception as e:
                logger.warning(f"Local vLLM failed: {e}")

        # 3. Frontier APIs (Claude > GPT-4o > Gemini) for high-value tasks
        if task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            if os.getenv("ANTHROPIC_API_KEY"):
                try:
                    from anthropic import Anthropic
                    if not self.anthropic_client:
                        self.anthropic_client = Anthropic()
                    resp = self.anthropic_client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4096,
                        temperature=temperature,
                        messages=[{"role": "user", "content": task}]
                    )
                    logger.info(f"Used Claude 3.5 Sonnet for {task_type}")
                    return resp.content[0].text
                except Exception as e:
                    logger.warning(f"Anthropic failed: {e}")

            if os.getenv("OPENAI_API_KEY"):
                try:
                    from openai import OpenAI
                    if not self.openai_client:
                        self.openai_client = OpenAI()
                    resp = self.openai_client.chat.completions.create(
                        model="gpt-4o",
                        temperature=temperature,
                        max_tokens=4096,
                        messages=[{"role": "user", "content": task}]
                    )
                    logger.info(f"Used GPT-4o for {task_type}")
                    return resp.choices[0].message.content
                except Exception as e:
                    logger.warning(f"OpenAI failed: {e}")

        # 4. External endpoint fallback (Chutes)
        if self.custom_endpoint:
            return self._call_external_endpoint(task, temperature, preferred)

        return "[NO COMPUTE AVAILABLE — Check keys / Chutes / Local setup]"

    def _call_external_endpoint(self, task: str, temperature: float = 0.0, preferred_model: str = None) -> str:
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "task": task,
                    "temperature": temperature,
                    "max_tokens": 2048,
                    "preferred_model": preferred_model
                }
                response = requests.post(self.custom_endpoint, json=payload, timeout=180)
                response.raise_for_status()
                data = response.json()
                return data.get("response", str(data))
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return f"[Endpoint Error] {str(e)}"
                time.sleep(2 ** attempt)
        return "[External Compute Failed]"

    def get_status(self):
        return f"Source: {self.compute_source} | Quasar: {'ON' if self.quasar_enabled else 'OFF'}"
