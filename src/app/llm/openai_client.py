from __future__ import annotations
import os, time
from typing import Any, Dict
import requests

from ..config import SETTINGS
from .base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, model: str, api_key: str | None) -> None:
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não configurada.")
        self.api_key = api_key
        self.model = model
        self.name = "chatgpt"

    def generate(self, prompt: str, **params: Any) -> str:
        # Implementado com a API de Chat Completions compatível
        # Evita dependência direta do SDK para simplicidade
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(params.get("temperature", 0.7)),
            "max_tokens": int(params.get("max_tokens", 512)),
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=SETTINGS.timeout_s)
        resp.raise_for_status()
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Falha ao ler resposta OpenAI: {e}")