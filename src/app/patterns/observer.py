from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any, List

@dataclass(frozen=True)
class SelectionEvent:
    question: str
    winner_model: str
    explanation: str
    scores: dict[str, float]
    responses: dict[str, str]

class Observer(Protocol):
    def update(self, event: SelectionEvent) -> None: ...

class ResultSubject:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, obs: Observer) -> None:
        self._observers.append(obs)

    def detach(self, obs: Observer) -> None:
        self._observers = [o for o in self._observers if o is not obs]

    def notify(self, event: SelectionEvent) -> None:
        for o in list(self._observers):
            o.update(event)