# agents/tools/compute.py
# Optimized Compute Router with Quasar + OpenRouter + Local + Direct APIs

import os
import requests
import time
from pathlib import Path
from typing import Any, Dict
import logging

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

    def choose_model(self, task_type: str) -> str:
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

    def set_compute_source(self, source: str, endpoint: str = None):
        self.compute_source = source
        self.custom_endpoint = endpoint
        self.use_local = (source == "local")

    def enable_quasar(self, enabled: bool = True):
        self.quasar_enabled = enabled

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium") -> str:
        
        # 1. Quasar (preferred for high-value tasks)
        if self.quasar_enabled and task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            if self._ensure_quasar_downloaded():
                try:
                    if self.quasar_llm is None:
                        from vllm import LLM, SamplingParams
                        self.quasar_llm = LLM(model=str(self.quasar_cache_dir), trust_remote_code=True, gpu_memory_utilization=0.85)
                    sampling = SamplingParams(temperature=temperature, max_tokens=4096)
                    outputs = self.quasar_llm.generate(task, sampling)
                    logger.info(f"[Quasar] Used for {task_type}")
                    return outputs[0].outputs[0].text.strip()
                except Exception as e:
                    logger.warning(f"Quasar failed: {e}")

        # 2. OpenRouter (strong unified fallback / miner preference)
        if os.getenv("OPENROUTER_API_KEY"):
            try:
                from openai import OpenAI
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    default_headers={
                        "HTTP-Referer": "https://github.com/jbequ5/Enigma-Machine-Miner",
                        "X-OpenRouter-Title": "Enigma Miner",
                    }
                )
                model = "anthropic/claude-3.5-sonnet" if task_type in ["planning","orchestration","adaptation","re_adapt"] else "openai/gpt-4o-mini"
                
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": task}],
                    temperature=temperature,
                    max_tokens=4096
                )
                logger.info(f"[OpenRouter] Used {model} for {task_type}")
                return resp.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenRouter failed: {e}")

        # 3. Local vLLM
        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    logger.info(f"[Local vLLM] Used for {task_type}")
                    return str(response)
            except Exception as e:
                logger.warning(f"Local vLLM failed: {e}")

        # 4. Direct frontier APIs (last resort)
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                client = Anthropic()
                resp = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4096,
                    temperature=temperature,
                    messages=[{"role": "user", "content": task}]
                )
                logger.info(f"[Claude Direct] Used for {task_type}")
                return resp.content[0].text
            except Exception:
                pass

        # 5. External endpoint (Chutes)
        if self.custom_endpoint:
            return self._call_external_endpoint(task, temperature)

        return "[NO COMPUTE AVAILABLE — Check API keys]"

    def _ensure_quasar_downloaded(self):
        if self.quasar_cache_dir.exists() and any(self.quasar_cache_dir.iterdir()):
            return True
        try:
            from huggingface_hub import snapshot_download
            logger.info("📥 Auto-downloading Quasar model...")
            snapshot_download(repo_id=self.quasar_model_id, local_dir=str(self.quasar_cache_dir), local_dir_use_symlinks=False)
            logger.info("✅ Quasar downloaded")
            return True
        except Exception as e:
            logger.error(f"Quasar download failed: {e}")
            return False

    def _call_external_endpoint(self, task: str, temperature: float = 0.0) -> str:
        for attempt in range(self.max_retries):
            try:
                payload = {"task": task, "temperature": temperature, "max_tokens": 2048}
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
        return f"Source: {self.compute_source} | Quasar: {'ON' if self.quasar_enabled else 'OFF'} | OpenRouter: {'ENABLED' if os.getenv('OPENROUTER_API_KEY') else 'DISABLED'}"
