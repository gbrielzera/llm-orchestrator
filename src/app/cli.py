# Em: API/src/app/cli.py

from __future__ import annotations
import argparse
import logging
from typing import List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import SETTINGS
from .utils.logging_setup import setup_logging
from .patterns.factory import LLMClientFactory
from .patterns.command import QueryCommand
from .patterns.strategy import CombinedStrategy, LengthStrategy, KeywordStrategy, EvaluationStrategy
# AJUSTE 1: O Observer não é mais necessário aqui, pois a lógica de notificação foi removida.
# from .patterns.observer import ResultSubject, Observer, SelectionEvent
# AJUSTE 2: Importar a classe correta.
from .evaluation.selector import ResponseEvaluator

console = Console()

# A classe ConsoleObserver foi movida para o final para manter a lógica principal agrupada,
# mas sua funcionalidade foi integrada ao loop principal `run`.

def build_strategy(args: argparse.Namespace) -> EvaluationStrategy:
    if args.strategy == "length":
        return LengthStrategy(target_len=args.target_len)
    elif args.strategy == "keyword":
        kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
        return KeywordStrategy(kws)
    else:
        # Para a estratégia combinada, também passamos as palavras-chave, se houver.
        kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
        return CombinedStrategy(length=args.target_len, keywords=kws)

def run(question: str, models: List[str], strategy: EvaluationStrategy, debug: bool=False) -> None:
    setup_logging(logging.DEBUG if debug else logging.INFO)

    # Factory
    clients = LLMClientFactory.create_all(models)

    # Executa comandos (Command)
    responses: Dict[str, str] = {}
    for name, client in clients.items():
        cmd = QueryCommand(client=client, prompt=question, params={"temperature":0.6, "max_tokens":512})
        try:
            text = cmd.execute()
        except Exception as e:
            text = f"[ERRO] {type(e).__name__}: {e}"
        responses[name] = text

    # AJUSTE 3: Usar a nova classe ResponseEvaluator.
    evaluator = ResponseEvaluator(strategy=strategy)
    # O método agora retorna diretamente o vencedor e os scores.
    winner_model, scores = evaluator.evaluate_responses(question, responses)

    # Apresentação dos scores (lógica do antigo Observer)
    table = Table(title="Pontuações por modelo", show_lines=True)
    table.add_column("Modelo", justify="left")
    table.add_column("Score", justify="right")
    if scores:
        for m, s in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
            table.add_row(m, f"{s:.3f}")
    console.print(table)
    
    # Construção da explicação
    explanation = f"Pergunta: {question} | Modelo vencedor: {winner_model} | Ranking: "
    if scores:
        ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        explanation += ", ".join(f"{m}={s:.3f}" for m,s in ordered)
    console.print(Panel.fit(explanation, title="Explicação da escolha", border_style="green"))


    # Apresentação final das respostas
    for model, text in responses.items():
        border_style = "cyan" if model == winner_model else "blue"
        console.print(Panel(text, title=f"Resposta de {model}", border_style=border_style))
    console.print(Panel.fit(f"Vencedor: [bold]{winner_model}[/bold]", title="Resultado", border_style="magenta"))

def main() -> None:
    parser = argparse.ArgumentParser(description="CLI que compara ChatGPT e outro LLM usando padrões de projeto.")
    parser.add_argument("question", type=str, help="Pergunta a ser enviada aos modelos.")
    parser.add_argument("--models", type=str, default="chatgpt,hf", help="Lista de modelos separados por vírgula (chatgpt,hf).")
    parser.add_argument("--strategy", type=str, choices=["combined","length","keyword"], default="combined", help="Estratégia de avaliação.")
    parser.add_argument("--target-len", type=int, default=180, help="Tamanho alvo para a estratégia de comprimento.")
    parser.add_argument("--keywords", type=str, default="", help="Palavras-chave separadas por vírgula para a estratégia baseada em termos.")
    parser.add_argument("--debug", action="store_true", help="Habilita logs em nível DEBUG.")
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    strategy = build_strategy(args)
    run(args.question, models, strategy, debug=args.debug)

if __name__ == "__main__":
    main()