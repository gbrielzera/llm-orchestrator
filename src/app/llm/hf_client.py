from __future__ import annotations
from typing import Any, Dict
import requests
from ..config import SETTINGS
from .base import LLMClient

class HFClient(LLMClient):
    def __init__(self, model: str, api_token: str | None) -> None:
        if not api_token:
            raise RuntimeError("HF_API_TOKEN não configurado.")
        self.api_token = api_token
        self.model = model
        self.name = "hf"

    def generate(self, prompt: str, **params: Any) -> str:
        # Usa a Inference API de text-generation
        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload: Dict[str, Any] = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": int(params.get("max_tokens", 256)),
                "temperature": float(params.get("temperature", 0.7)),
                "return_full_text": False,
            }
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=SETTINGS.timeout_s)
        resp.raise_for_status()
        data = resp.json()
        # Converte formatos possíveis
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"].strip()
        raise RuntimeError(f"Formato inesperado da resposta HF: {str(data)[:200]}")