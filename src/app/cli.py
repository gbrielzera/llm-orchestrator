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
# AJUSTE 1: Re-importar as classes do Observer
from .patterns.observer import ResultSubject, Observer, SelectionEvent
# AJUSTE 2: Importar o ResponseEvaluator
from .evaluation.selector import ResponseEvaluator

console = Console()

# AJUSTE 3: Restaurar a classe ConsoleObserver
class ConsoleObserver(Observer):
    """Um observer que imprime os resultados no console."""
    def update(self, event: SelectionEvent) -> None:
        console.print("\n--- [ Análise da Seleção ] ---")
        table = Table(title="Pontuações por modelo", show_lines=True)
        table.add_column("Modelo", justify="left")
        table.add_column("Score", justify="right")
        
        if event.scores:
            for m, s in sorted(event.scores.items(), key=lambda kv: kv[1], reverse=True):
                table.add_row(m, f"{s:.3f}")
        
        console.print(table)
        console.print(Panel.fit(event.explanation, title="Explicação da escolha", border_style="green"))
        console.print("--- [ Fim da Análise ] ---\n")


def build_strategy(args: argparse.Namespace) -> EvaluationStrategy:
    # (Esta função não muda)
    if args.strategy == "length":
        return LengthStrategy(target_len=args.target_len)
    elif args.strategy == "keyword":
        kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
        return KeywordStrategy(kws)
    else:
        kws = [k.strip() for k in (args.keywords or "").split(",") if k.strip()]
        return CombinedStrategy(length=args.target_len, keywords=kws)

def run(question: str, models: List[str], strategy: EvaluationStrategy, debug: bool=False) -> None:
    setup_logging(logging.DEBUG if debug else logging.INFO)

    clients = LLMClientFactory.create_all(models)

    # AJUSTE 4: Criar o Subject e o Observer
    subject = ResultSubject()
    observer = ConsoleObserver()
    subject.attach(observer)

    responses: Dict[str, str] = {}
    for name, client in clients.items():
        cmd = QueryCommand(client=client, prompt=question, params={"temperature":0.6, "max_tokens":512})
        try:
            text = cmd.execute()
        except Exception as e:
            text = f"[ERRO] {type(e).__name__}: {e}"
        responses[name] = text

    # AJUSTE 5: Criar o avaliador e passar o 'subject' para ele
    evaluator = ResponseEvaluator(strategy=strategy, subject=subject)
    # A chamada ao método 'choose' irá NOTIFICAR o ConsoleObserver, que imprimirá a análise
    result = evaluator.choose(question, responses)

    # AJUSTE 6: A apresentação da análise agora é automática (via observer).
    # O final do script apenas apresenta as respostas e o vencedor.
    console.print("--- [ Respostas Completas ] ---")
    for model, text in responses.items():
        border_style = "cyan" if model == result.winner_model else "blue"
        console.print(Panel(text, title=f"Resposta de {model}", border_style=border_style))
    
    console.print(Panel.fit(f"Vencedor: [bold]{result.winner_model}[/bold]", title="Resultado Final", border_style="magenta"))

# A função main() não precisa de alterações
def main() -> None:
    parser = argparse.ArgumentParser(description="CLI que compara ChatGPT e outro LLM usando padrões de projeto.")
    parser.add_argument("question", type=str, help="Pergunta a ser enviada aos modelos.")
    parser.add_argument("--models", type=str, default="chatgpt,gemini", help="Lista de modelos separados por vírgula (chatgpt,gemini).")
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