# agents/tools/compute.py
# Optimized Compute Router with Reliable Local GPU (Ollama) + Quasar + OpenRouter + Direct APIs
# Updated for full compatibility with ArbosManager and Streamlit UI — Local GPU now works reliably without external keys

import os
import requests
import time
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Try to import Ollama (primary local path)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama Python package not installed. Local GPU fallback limited.")

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
            "self_critique": "fast",
        }

    def choose_model(self, task_type: str) -> str:
        if task_type in ["planning", "orchestration", "adaptation", "re_adapt"]:
            return "best"
        return self.model_preferences.get(task_type, "fast")


class ComputeRouter:
    def __init__(self):
        self.compute_source = "local_gpu"
        self.custom_endpoint = None
        self.llm_router = LLMRouter()
        self.max_retries = 3
        self.quasar_enabled = True
        self.quasar_llm = None
        self.quasar_model_id = "silx-ai/Quasar-10B"
        self.quasar_cache_dir = Path("models/Quasar-10B")
        self.default_local_model = "llama3.2"  # Fast & capable for most planning tasks

    def set_mode(self, mode: str, model: Optional[str] = None):
        """Main entry for setting compute mode from Streamlit / ArbosManager."""
        if model:
            self.default_local_model = model
        if mode in ["local_gpu", "local"]:
            self.compute_source = "local_gpu"
            logger.info(f"✅ ComputeRouter set to Local GPU (Ollama model: {self.default_local_model})")
        else:
            self.compute_source = mode
            logger.info(f"Compute source set to: {mode}")

    def set_compute_source(self, source: str, endpoint: Optional[str] = None):
        """Backward compatibility with existing code."""
        self.compute_source = source
        self.custom_endpoint = endpoint
        if source in ["local", "local_gpu"]:
            self.set_mode("local_gpu")

    def enable_quasar(self, enabled: bool = True):
        self.quasar_enabled = enabled
        logger.info(f"Quasar Long-Context Attention: {'ENABLED' if enabled else 'DISABLED'}")

    def call_llm(self, prompt: str, system_prompt: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: int = 2048, 
                 task_type: str = "subtask") -> str:
        """Primary unified method used by ArbosManager — prioritizes reliable Local GPU."""
        
        # 1. Local GPU via Ollama (strongest & default path — no API keys needed)
        if self.compute_source in ["local_gpu", "local"]:
            if OLLAMA_AVAILABLE:
                try:
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})

                    response = ollama.chat(
                        model=self.default_local_model,
                        messages=messages,
                        options={
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    )
                    output = response['message']['content'].strip()
                    logger.info(f"[Local Ollama] Used {self.default_local_model} for {task_type}")
                    return output
                except Exception as e:
                    logger.warning(f"Ollama call failed: {e}. Ensure 'ollama run {self.default_local_model}' is running.")
            else:
                return f"[Ollama not installed] Install with: pip install ollama and run 'ollama run {self.default_local_model}'"

        # 2. Quasar (high-value tasks only)
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
                    sampling = SamplingParams(temperature=temperature, max_tokens=max_tokens)
                    outputs = self.quasar_llm.generate(prompt, sampling)
                    logger.info(f"[Quasar] Used for {task_type}")
                    return outputs[0].outputs[0].text.strip()
                except Exception as e:
                    logger.warning(f"Quasar failed: {e}")

        # 3. OpenRouter (strong cloud fallback)
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
                
                messages = [{"role": "user", "content": prompt}]
                if system_prompt:
                    messages.insert(0, {"role": "system", "content": system_prompt})
                
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.info(f"[OpenRouter] Used {model} for {task_type}")
                return resp.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenRouter failed: {e}")

        # 4. Direct Anthropic (Claude)
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                from anthropic import Anthropic
                client = Anthropic()
                messages = [{"role": "user", "content": prompt}]
                if system_prompt:
                    messages.insert(0, {"role": "system", "content": system_prompt})
                
                resp = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages
                )
                logger.info(f"[Claude Direct] Used for {task_type}")
                return resp.content[0].text.strip()
            except Exception as e:
                logger.warning(f"Claude direct failed: {e}")

        # 5. Custom / Chutes external endpoint
        if self.custom_endpoint:
            return self._call_external_endpoint(prompt, temperature)

        # Final safe fallback
        return f"[NO COMPUTE AVAILABLE — Start Ollama with 'ollama run {self.default_local_model}' or add API keys for OpenRouter/Anthropic]"

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium") -> str:
        """Legacy compatibility method — routes to the new unified call_llm."""
        return self.call_llm(
            prompt=task, 
            temperature=temperature, 
            task_type=task_type,
            max_tokens=4096 if task_type in ["planning", "orchestration"] else 2048
        )

    def _ensure_quasar_downloaded(self):
        if self.quasar_cache_dir.exists() and any(self.quasar_cache_dir.iterdir()):
            return True
        try:
            from huggingface_hub import snapshot_download
            logger.info("📥 Auto-downloading Quasar-10B model (this may take time)...")
            snapshot_download(
                repo_id=self.quasar_model_id, 
                local_dir=str(self.quasar_cache_dir), 
                local_dir_use_symlinks=False
            )
            logger.info("✅ Quasar model downloaded successfully")
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
                    return f"[External Endpoint Error] {str(e)}"
                time.sleep(2 ** attempt)
        return "[External Compute Failed]"

    def get_status(self):
        return f"Source: {self.compute_source} | Quasar: {'ON' if self.quasar_enabled else 'OFF'} | Local Ollama: {'Ready' if OLLAMA_AVAILABLE else 'Not installed'}"

# Global singleton instance used across the project
compute_router = ComputeRouter()
