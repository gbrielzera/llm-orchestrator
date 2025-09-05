# from __future__ import annotations
# from dataclasses import dataclass
# from typing import Dict, Tuple
# from ..patterns.strategy import EvaluationStrategy, CombinedStrategy
# from ..patterns.observer import ResultSubject, SelectionEvent

# @dataclass
# class SelectionResult:
#     winner_model: str
#     explanation: str
#     scores: Dict[str, float]

# class ResponseSelector:
#     def __init__(self, strategy: EvaluationStrategy | None = None, subject: ResultSubject | None = None) -> None:
#         self.strategy = strategy or CombinedStrategy()
#         self.subject = subject

#     def choose(self, question: str, responses: Dict[str, str]) -> SelectionResult:
#         scores: Dict[str, float] = {}
#         # baseline = resposta do primeiro modelo (para diversidade)
#         baseline = next(iter(responses.values())) if responses else ""
#         context = {"baseline": baseline}

#         for model, text in responses.items():
#             scores[model] = float(self.strategy.score(question, text, context=context))

#         winner = max(scores.items(), key=lambda kv: kv[1])[0] if scores else ""
#         explanation = self._build_explanation(question, winner, responses, scores)

#         if self.subject:
#             event = SelectionEvent(question, winner, explanation, scores, responses)
#             self.subject.notify(event)

#         return SelectionResult(winner, explanation, scores)

#     @staticmethod
#     def _build_explanation(question: str, winner: str, responses: Dict[str, str], scores: Dict[str, float]) -> str:
#         parts = [f"Pergunta: {question}", f"Modelo vencedor: {winner}"]
#         # Mostrar top2 critérios implicitamente via pontuações
#         ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
#         parts.append("Ranking de pontuações: " + ", ".join(f"{m}={s:.3f}" for m,s in ordered))
#         return " | ".join(parts)

# # Execução de teste rápida
# if __name__ == "__main__":
#     from ..patterns.strategy import CombinedStrategy
#     selector = ResponseSelector(CombinedStrategy())
#     resps = {"chatgpt":"Resposta A breve com termos X e Y.","hf":"Resposta B detalhada com termos Y e Z."}
#     out = selector.choose("Teste?", resps)
#     print(out)

# Em: src/app/evaluation/selector.py
from typing import Dict
from app.patterns.strategy import EvaluationStrategy

class ResponseEvaluator:
    def __init__(self, strategy: EvaluationStrategy):
        self._strategy = strategy

    def evaluate_responses(self, question: str, responses: Dict[str, str]) -> tuple[str, Dict[str, float]]:
        """
        Avalia um dicionário de respostas usando a estratégia fornecida.

        Args:
            question (str): A pergunta original do usuário.
            responses (Dict[str, str]): Um dicionário onde a chave é o nome do modelo
                                       e o valor é a resposta textual.

        Returns:
            A tuple contendo o nome do modelo vencedor e um dicionário com as pontuações de todos.
        """
        if not responses:
            return "Nenhum", {}

        scores: Dict[str, float] = {}
        
        # Para a DiversityStrategy, podemos usar a primeira resposta como baseline para as outras.
        # Pegamos a primeira resposta válida que não seja um erro.
        baseline_response = next(
            (resp for resp in responses.values() if "[erro]" not in resp.lower()), 
            ""
        )
        
        for model, response in responses.items():
            # Criamos um contexto para cada avaliação.
            # A DiversityStrategy usará o 'baseline'.
            context = {"baseline": baseline_response}
            
            # Chamamos o método .score() com todos os argumentos necessários.
            scores[model] = self._strategy.score(question, response, context)
        
        # Encontra o modelo com a maior pontuação
        winner = max(scores, key=scores.get)
        
        return winner, scores