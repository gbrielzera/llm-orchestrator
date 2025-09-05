# Em: API/src/app/patterns/factory.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Type
from ..config import SETTINGS
from ..llm.base import LLMClient
from ..llm.openai_client import OpenAIClient
from ..llm.mock_client import MockClient
# IMPORTAR O NOVO CLIENTE
from ..llm.gemini_client import GeminiClient

@dataclass
class LLMClientFactory:
    @staticmethod
    def create_all(models: list[str]) -> Dict[str, LLMClient]:
        clients: Dict[str, LLMClient] = {}
        for m in models:
            m_low = m.lower().strip()
            if SETTINGS.mock_mode:
                clients[m_low] = MockClient(name=m_low)
            elif m_low in {"chatgpt","openai","gpt"}:
                clients[m_low] = OpenAIClient(model=SETTINGS.openai_model, api_key=SETTINGS.openai_api_key)
            # REMOVER HF E ADICIONAR GEMINI
            elif m_low in {"gemini", "google"}:
                clients[m_low] = GeminiClient(model=SETTINGS.gemini_model, api_key=SETTINGS.gemini_api_key)
            else:
                raise ValueError(f"Modelo desconhecido: {m}")
        return clients