# LLM Orchestrator (CLI)

Integra **ChatGPT** (OpenAI) e outro **LLM** (via Hugging Face Inference API) para comparar respostas e selecionar a melhor com base em estratégias de avaliação. Implementa os padrões **Factory**, **Command**, **Strategy** e **Observer**.

## Requisitos
- Python 3.10+
- Conta/Token na OpenAI (`OPENAI_API_KEY`) para ChatGPT.
- Conta/Token na Hugging Face (`HF_API_TOKEN`) para o segundo LLM.

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```
(ou `pip install -r requirements.txt` se preferir).

## Configuração
Crie um arquivo `.env` com as chaves:
```
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini   # exemplo; ajuste conforme seu plano
HF_API_TOKEN=...
HF_MODEL=tiiuae/falcon-7b-instruct   # exemplo; ajuste para um modelo de geração de texto
```

Você também pode executar em **modo mock** (sem chamadas externas) para testes/demonstração:
```
MOCK_MODE=true
```

## Uso (CLI)
Perguntar usando os dois modelos com a estratégia combinada (padrão):
```bash
llm-orchestrator "Explique o que é entropia em termos simples"
```

Escolher estratégia explicitamente:
```bash
llm-orchestrator "Explique entropia" --strategy keyword --keywords "energia,desordem,termodinâmica"
llm-orchestrator "Explique entropia" --strategy length --target-len 120
```

Selecionar modelos e ativar debug verboso:
```bash
llm-orchestrator "Explique entropia" --models chatgpt,hf --debug
```

Rodar em modo **mock** (sem API):
```bash
MOCK_MODE=true llm-orchestrator "Explique entropia"
```

## Arquitetura (padrões de projeto)
- **Factory**: `LLMClientFactory` cria clientes `OpenAIClient` e `HFClient` (ou `MockClient`) com base na config/env.
- **Command**: `QueryCommand` encapsula a requisição (prompt, params) e executa no cliente apropriado.
- **Strategy**: estratégias em `strategy.py` (length, keyword, diversity, combined) pontuam respostas; `selector.py` escolhe a melhor.
- **Observer**: `ResultSubject` notifica observadores (`ConsoleObserver`, etc.) quando a resposta escolhida muda.

## Demonstração
1. Configure `.env` com seus tokens **ou** `MOCK_MODE=true`.
2. Execute o comando de exemplo acima.
3. Veja no terminal as respostas de cada modelo, as pontuações e a **explicação da escolha**.

## Testes rápidos
```bash
python -m app.evaluation.selector
python -m app.llm.base
```

## Vídeo sugerido
Grave a execução: mostrar `MOCK_MODE=true` + uma execução real com as chaves, destacando as camadas e prints das pontuações.

## Licença
MIT