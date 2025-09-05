# Em: src/app/patterns/strategy.py

from __future__ import annotations
# AJUSTE 1: Corrigido 'abc' para 'ABC'
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Tuple

# AJUSTE 2: A classe base agora define o método 'score' com a assinatura completa.
# Isso garante que todas as estratégias filhas sigam o mesmo "contrato".
class EvaluationStrategy(ABC):
    """Interface para as estratégias de avaliação."""
    @abstractmethod
    def score(self, question: str, response: str, context: Dict | None = None) -> float:
        """
        Calcula uma pontuação para uma dada resposta.

        Args:
            question (str): A pergunta original do usuário.
            response (str): A resposta do modelo de linguagem.
            context (Dict | None): Um dicionário opcional para dados contextuais,
                                   como respostas de outros modelos (usado por DiversityStrategy).

        Returns:
            float: A pontuação calculada, geralmente entre 0.0 e 1.0.
        """
        pass

# As classes abaixo estavam corretas, apenas não correspondiam à interface.
# Agora elas a implementam corretamente.

class LengthStrategy(EvaluationStrategy):
    def __init__(self, target_len: int = 200):
        self.target = target_len

    def score(self, question: str, response: str, context: Dict | None = None) -> float:
        n = len(response)
        # Retorna um score maior quanto mais perto do tamanho alvo.
        return 1.0 / (1.0 + abs(n - self.target))

class KeywordStrategy(EvaluationStrategy):
    def __init__(self, keywords: Iterable[str]):
        self.keywords = [k.strip().lower() for k in keywords if k.strip()]

    def score(self, question: str, response: str, context: Dict | None = None) -> float:
        text = response.lower()
        if not self.keywords:
            return 0.0 # Retorna 0 se não houver palavras-chave para avaliar.
        hits = sum(1 for k in self.keywords if k in text)
        return hits / len(self.keywords)

class DiversityStrategy(EvaluationStrategy):
    def score(self, question: str, response: str, context: Dict | None = None) -> float:
        baseline = (context or {}).get("baseline", "")
        if not baseline:
            return 0.5  # Se não houver baseline, retorna uma pontuação neutra.
        
        a = set(baseline.lower().split())
        b = set(response.lower().split())
        intersection = len(a.intersection(b))
        union = len(a.union(b))
        
        if union == 0:
            return 1.0 # Se ambas as strings estiverem vazias, são idênticas.
            
        jaccard_similarity = intersection / union
        # A pontuação é a "distância", ou seja, 1 - similaridade.
        return 1.0 - jaccard_similarity

class CombinedStrategy(EvaluationStrategy):
    def __init__(self, length: int = 180, keywords: Iterable[str] | None = None, w_len=0.3, w_kw=0.5, w_div=0.2):
        self.len_s = LengthStrategy(length)
        self.kw_s = KeywordStrategy(keywords or [])
        self.div_s = DiversityStrategy()
        # Normalizando os pesos para garantir que somem 1
        total_w = w_len + w_kw + w_div
        self.w_len = w_len / total_w
        self.w_kw = w_kw / total_w
        self.w_div = w_div / total_w

    def score(self, question: str, response: str, context: Dict | None = None) -> float:
        # Penaliza respostas de erro antes de qualquer outra avaliação.
        if "[erro]" in response.lower() or "error" in response.lower():
            return 0.0

        score_len = self.len_s.score(question, response, context)
        score_kw = self.kw_s.score(question, response, context)
        score_div = self.div_s.score(question, response, context)

        final_score = (
            self.w_len * score_len +
            self.w_kw * score_kw +
            self.w_div * score_div
        )
        return final_score