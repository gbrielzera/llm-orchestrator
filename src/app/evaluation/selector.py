from __future__ import annotations
from typing import Dict
from dataclasses import dataclass

from ..patterns.strategy import EvaluationStrategy
from ..patterns.observer import ResultSubject, SelectionEvent

@dataclass(frozen=True)
class SelectionResult:
    winner_model: str
    explanation: str
    scores: Dict[str, float]

class ResponseEvaluator:
    def __init__(self, strategy: EvaluationStrategy, subject: ResultSubject | None = None):
        self._strategy = strategy
        self.subject = subject

    def choose(self, question: str, responses: Dict[str, str]) -> SelectionResult:
        if not responses:
            return SelectionResult("Nenhum", "Sem respostas para avaliar.", {})

        scores: Dict[str, float] = {}
        baseline_response = next(
            (resp for resp in responses.values() if "[erro]" not in resp.lower()), ""
        )
        
        for model, response in responses.items():
            context = {"baseline": baseline_response}
            scores[model] = self._strategy.score(question, response, context)
        
        winner = max(scores, key=scores.get) if scores else "Nenhum"
        explanation = self._build_explanation(question, winner, scores)

        if self.subject:
            event = SelectionEvent(
                question=question, 
                winner_model=winner, 
                explanation=explanation, 
                scores=scores, 
                responses=responses
            )
            self.subject.notify(event)
        
        return SelectionResult(winner, explanation, scores)

    @staticmethod
    def _build_explanation(question: str, winner: str, scores: Dict[str, float]) -> str:
        parts = [f"Pergunta: {question}", f"Modelo vencedor: {winner}"]
        if scores:
            ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            parts.append("Ranking de pontuações: " + ", ".join(f"{m}={s:.3f}" for m,s in ordered))
        return " | ".join(parts)
