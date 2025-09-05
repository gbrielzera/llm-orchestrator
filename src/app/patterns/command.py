from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict
from ..llm.base import LLMClient

@dataclass
class QueryCommand:
    client: LLMClient
    prompt: str
    params: Dict[str, Any] = field(default_factory=dict)

    def execute(self) -> str:
        return self.client.generate(self.prompt, **self.params)