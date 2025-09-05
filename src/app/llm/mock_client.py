from __future__ import annotations
from typing import Any
from .base import LLMClient

class MockClient(LLMClient):
    def __init__(self, name: str = "mock") -> None:
        self.name = name

    def generate(self, prompt: str, **params: Any) -> str:
        # respostas simples previsíveis para demonstração
        if "entropia" in prompt.lower():
            if self.name.startswith("chat"):
                return "Entropia mede a dispersão de energia e o número de microestados possíveis; em termos simples, é um jeito de quantificar a desordem."
            else:
                return "Entropia é uma grandeza da termodinâmica associada à irreversibilidade; sistemas isolados tendem a estados mais prováveis (maior entropia)."
        return f"[{self.name}] Resposta simulada ao prompt: {prompt[:80]}..."