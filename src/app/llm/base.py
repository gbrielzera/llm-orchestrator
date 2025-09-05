from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class LLMClient(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str, **params: Any) -> str:
        ...

# Execução rápida de teste manual (sem dependências)
if __name__ == "__main__":
    class Dummy(LLMClient):
        name="dummy"
        def generate(self, prompt: str, **params: Any) -> str:
            return f"Echo({self.name}): {prompt}"
    print(Dummy().generate("testando"))