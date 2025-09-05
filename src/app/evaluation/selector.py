# Em: src/app/evaluation/selector.py
from __future__ import annotations
from typing import Dict
from dataclasses import dataclass

# Importações necessárias para os padrões de projeto
from ..patterns.strategy import EvaluationStrategy
from ..patterns.observer import ResultSubject, SelectionEvent

@dataclass(frozen=True)
class SelectionResult:
    """Um objeto para encapsular o resultado da seleção de forma limpa."""
    winner_model: str
    explanation: str
    scores: Dict[str, float]

class ResponseEvaluator:
    """
    Esta classe avalia um conjunto de respostas de LLMs, escolhe a melhor
    com base em uma Strategy e notifica os Observers sobre o resultado.
    """
    def __init__(self, strategy: EvaluationStrategy, subject: ResultSubject | None = None):
        """
        Inicializa o avaliador com uma estratégia e um 'subject' opcional para notificações.
        """
        self._strategy = strategy
        self.subject = subject

    def choose(self, question: str, responses: Dict[str, str]) -> SelectionResult:
        """
        Avalia as respostas, escolhe um vencedor e notifica os observadores.
        """
        if not responses:
            return SelectionResult("Nenhum", "Sem respostas para avaliar.", {})

        scores: Dict[str, float] = {}
        # Define uma resposta de base para a estratégia de diversidade
        baseline_response = next(
            (resp for resp in responses.values() if "[erro]" not in resp.lower()), ""
        )
        
        for model, response in responses.items():
            context = {"baseline": baseline_response}
            scores[model] = self._strategy.score(question, response, context)
        
        # Encontra o vencedor
        winner = max(scores, key=scores.get) if scores else "Nenhum"
        explanation = self._build_explanation(question, winner, scores)

        # Se um 'subject' foi fornecido, cria e notifica um evento com o resultado
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
        """Constrói uma string de explicação para o resultado."""
        parts = [f"Pergunta: {question}", f"Modelo vencedor: {winner}"]
        if scores:
            ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            parts.append("Ranking de pontuações: " + ", ".join(f"{m}={s:.3f}" for m,s in ordered))
        return " | ".join(parts)
