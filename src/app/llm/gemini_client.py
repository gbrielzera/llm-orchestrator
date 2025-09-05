# Em: API/src/app/llm/gemini_client.py
from __future__ import annotations
import os
from typing import Any, Dict
import requests
import json

from ..config import SETTINGS
from .base import LLMClient

class GeminiClient(LLMClient):
    def __init__(self, model: str, api_key: str | None) -> None:
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY não configurada.")
        self.api_key = api_key
        self.model = model
        self.name = "gemini"

    def generate(self, prompt: str, **params: Any) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {
                "temperature": float(params.get("temperature", 0.7)),
                "maxOutputTokens": int(params.get("max_tokens", 512)),
            }
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=SETTINGS.timeout_s)

        resp.raise_for_status() 

        data = resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            print("Resposta inesperada da API Gemini:", json.dumps(data, indent=2))
            raise RuntimeError(f"Falha ao ler resposta do Gemini: {e}")