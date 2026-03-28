# agents/tools/compute.py
# Final version with proactive remote VRAM check

import torch
import requests
import time
from typing import Any, Dict
import numpy as np
from validation_oracle import ValidationOracle
from trajectories.trajectory_vector_db import vector_db
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def compute_energy(candidate: dict, oracle: ValidationOracle, rank: int = 8) -> float:
    val_result = oracle.run(candidate.get("solution", {}))
    candidate["validation_score"] = val_result["validation_score"]
    
    novelty = candidate.get("novelty_proxy", 0.5)
    verifier = val_result["validation_score"]
    base_cost = candidate.get("est_compute", 1.0)
    cost = base_cost * (rank / 64.0) + 1e-5
    energy = (novelty * verifier) / cost
    
    logger.info(f"EGGROLL Energy: {energy:.4f} (rank={rank}, score={verifier:.4f}, cost={cost:.2f})")
    return energy

class LLMRouter:
    def __init__(self):
        self.model_preferences = {
            "planning": "best", "orchestration": "best", "subtask": "fast",
            "synthesis": "best", "verification": "fast", "toolhunter": "fast"
        }

    def choose_model(self, task_type: str, novelty_level: str = "medium", miner_preference: str = None) -> str:
        if miner_preference:
            return miner_preference
        if novelty_level == "high" or task_type in ["planning", "orchestration", "synthesis"]:
            return "best"
        return self.model_preferences.get(task_type, "fast")

class ComputeRouter:
    def __init__(self):
        self.compute_source = None
        self.custom_endpoint = None
        self.use_local = False
        self.llm_router = LLMRouter()
        self.max_retries = 3

    def set_compute_source(self, source: str, endpoint: str = None):
        self.compute_source = source
        self.custom_endpoint = endpoint
        if source == "local":
            self.use_local = torch.cuda.is_available()
        else:
            self.use_local = False

    def run_on_compute(self, task: str, temperature: float = 0.0, task_type: str = "subtask", 
                       novelty_level: str = "medium", miner_preferred_model: str = None) -> str:
        preferred_model = self.llm_router.choose_model(task_type, novelty_level, miner_preferred_model)

        if self.use_local:
            try:
                from agents.arbos_manager import get_vllm_llm
                llm = get_vllm_llm()
                if llm:
                    response = llm.generate(task, max_tokens=2048, temperature=temperature)
                    return response[0].text if hasattr(response[0], 'text') else str(response)
            except Exception:
                pass

        if self.custom_endpoint:
            if miner_preferred_model and not self.use_local:
                quantized = self._try_quantized_version(miner_preferred_model)
                if quantized != miner_preferred_model:
                    print(f"⚡ Using quantized version: {quantized} for hosted compute")
                    preferred_model = quantized
            return self._call_external_endpoint(task, temperature, preferred_model)

        return "[COMPUTE NOT CONFIGURED]"

    def _try_quantized_version(self, model_name: str) -> str:
        quantized_map = {
            "Llama-3-70B": "TheBloke/Llama-3-70B-Instruct-GPTQ-4bit",
            "Llama-3-8B": "TheBloke/Llama-3-8B-Instruct-GPTQ-4bit",
            "Mixtral-8x22B": "TheBloke/Mixtral-8x22B-Instruct-v0.1-GPTQ",
            "Qwen2-72B": "Qwen/Qwen2-72B-Instruct-GPTQ-4bit"
        }
        for key, q_version in quantized_map.items():
            if key.lower() in model_name.lower():
                return q_version
        return model_name

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
        # Proactive remote VRAM check (if endpoint supports it)
        try:
            if self.custom_endpoint:
                r = requests.get(self.custom_endpoint + "/status", timeout=5)
                if r.status_code == 200:
                    return r.json().get("vram_info", f"Source: {self.compute_source}")
        except:
            pass
        return f"Source: {self.compute_source} | Model routing active"
