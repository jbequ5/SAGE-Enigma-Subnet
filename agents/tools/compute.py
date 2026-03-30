# agents/tools/compute.py
# Lean & Intelligent ComputeRouter with Quasar + vLLM + Frontier APIs

import os
import requests
import time
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
            "synthesis": "best",
            "verification": "fast",
            "toolhunter": "fast",
        }

    def choose_model(self, task_type: str, novelty_level: str = "medium") -> str:
        if novelty_level == "high" or task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            return "best"
        return self.model_preferences.get(task_type, "fast")


class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False
        self.llm_router = LLMRouter()
        self.max_retries = 3
        self.quasar_enabled = False
        self.quasar_llm = None

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

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium") -> str:
        preferred = self.llm_router.choose_model(task_type, novelty_level)

        # 1. Quasar (best for long-context critical tasks)
        if self.quasar_enabled and task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            try:
                if self.quasar_llm is None:
                    from vllm import LLM, SamplingParams
                    self.quasar_llm = LLM(model="silx-ai/Quasar-10B", trust_remote_code=True)
                sampling = SamplingParams(temperature=temperature, max_tokens=4096)
                outputs = self.quasar_llm.generate(task, sampling)
                return outputs[0].outputs[0].text.strip()
            except Exception as e:
                logger.warning(f"Quasar failed, falling back: {e}")

        # 2. Local vLLM
        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception as e:
                logger.warning(f"Local vLLM failed: {e}")

        # 3. Frontier APIs (intelligent fallback - only for high-value tasks)
        if task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            # Claude first (best reasoning)
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
                    logger.info("Used Claude 3.5 Sonnet for high-value task")
                    return resp.content[0].text
                except Exception as e:
                    logger.warning(f"Anthropic failed: {e}")

            # GPT-4o second
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
                    logger.info("Used GPT-4o for high-value task")
                    return resp.choices[0].message.content
                except Exception as e:
                    logger.warning(f"OpenAI failed: {e}")

            # Gemini last
            if os.getenv("GEMINI_API_KEY"):
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
                    model = genai.GenerativeModel("gemini-1.5-pro")
                    resp = model.generate_content(task)
                    logger.info("Used Gemini 1.5 Pro for high-value task")
                    return resp.text
                except Exception as e:
                    logger.warning(f"Gemini failed: {e}")

        # 4. External endpoint (Chutes, etc.)
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
