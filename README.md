# **LLM Orchestrator (CLI)**

Esta aplicação CLI integra o **ChatGPT** (via API da OpenAI) e o **Gemini** (via API do Google AI) para comparar suas respostas a uma pergunta do usuário. A melhor resposta é selecionada com base em uma estratégia de avaliação personalizável.

O projeto foi construído utilizando os seguintes padrões de projeto: **Factory**, **Command**, **Strategy** e **Observer**, para garantir uma arquitetura flexível, robusta e de fácil manutenção.

## **Requisitos**

* Python 3.10+  
* Conta e Chave de API na [OpenAI](https://platform.openai.com/api-keys) (OPENAI\_API\_KEY).  
* Conta e Chave de API no [Google AI Studio](https://aistudio.google.com/app/apikey) (GEMINI\_API\_KEY).

## **Instalação**

1. **Crie e ative um ambiente virtual:**  
   python \-m venv .venv  
   \# Windows  
   .venv\\Scripts\\activate  
   \# macOS/Linux  
   source .venv/bin/activate

2. **Instale as dependências e o projeto em modo editável:**  
   pip install \-e .

## **Configuração**

Antes de executar, crie um arquivo chamado .env na raiz do projeto, seguindo o exemplo abaixo, e adicione suas chaves de API.

\# Chave da OpenAI para o ChatGPT  
OPENAI\_API\_KEY=sk-proj-SUA\_CHAVE\_DA\_OPENAI\_AQUI  
OPENAI\_MODEL=gpt-4o-mini

\# Chave do Google AI Studio para o Gemini  
GEMINI\_API\_KEY=AIzaSySUA\_CHAVE\_DO\_GEMINI\_AQUI  
GEMINI\_MODEL=gemini-1.5-flash-latest

\# Para rodar sem chamadas de API (respostas simuladas), mude para true  
MOCK\_MODE=false

## **Uso (CLI)**

A estrutura do comando é simples: llm-orchestrator "SUA PERGUNTA" \[OPÇÕES\]

#### **Exemplo Básico**

Perguntar aos dois modelos usando a estratégia de avaliação padrão ("combined"):

llm-orchestrator "Qual o maior prédio do mundo?" \--models chatgpt,gemini

#### **Controlando a Avaliação com Estratégias**

Você pode controlar como o "juiz" (nosso programa) avalia as respostas usando o argumento \--strategy.

**1\. Estratégia por Palavras-Chave (keyword)**

Prioriza a resposta que contém um conjunto específico de palavras.

llm-orchestrator "Explique o que é a fotossíntese" \--strategy keyword \--keywords "clorofila,luz,oxigênio"

**2\. Estratégia por Tamanho (length)**

Prioriza a resposta que tem o tamanho mais próximo de um alvo definido (em caracteres).

llm-orchestrator "Resuma o filme O Poderoso Chefão em uma frase" \--strategy length \--target-len 80

**3\. Estratégia Combinada (combined) \- Padrão**

Usa uma média ponderada de múltiplos critérios. Você pode ajustar os parâmetros das outras estratégias ao usá-la.

llm-orchestrator "Fale sobre a Roma Antiga" \--keywords "império,coliseu" \--target-len 200

#### **Outras Opções**

* **Ativar modo de depuração (verbose):**  
  llm-orchestrator "Qual sua pergunta?" \--debug

* Rodar em modo de simulação (sem API):  
  Altere MOCK\_MODE=true no arquivo .env. O programa usará respostas internas pré-definidas, ideal para testes rápidos e desenvolvimento offline.

## **Como a Avaliação Funciona?**

Quando você usa a estratégia padrão (combined), o programa atua como um juiz que avalia três aspectos de cada resposta para dar uma nota final. Os pesos são:

1. **Palavras-Chave (Peso: 50%):** Verifica se a resposta contém os termos que você definiu com \--keywords. É o critério mais importante para garantir a relevância do conteúdo.  
2. **Tamanho da Resposta (Peso: 30%):** Compara o tamanho da resposta com um "tamanho ideal" (padrão de 180 caracteres, ajustável com \--target-len). Este critério recompensa a objetividade.  
3. **Diversidade (Peso: 20%):** Compara as respostas entre si para evitar que sejam idênticas. Recompensa respostas que oferecem uma formulação ou perspectiva diferente.

A resposta com a maior nota final ponderada é declarada a vencedora.

## **Arquitetura (Padrões de Projeto)**

* **Factory**: LLMClientFactory cria os objetos de cliente (OpenAIClient, GeminiClient, MockClient) de forma centralizada e flexível.  
* **Command**: QueryCommand encapsula cada pergunta como um objeto, separando a configuração da execução.  
* **Strategy**: As classes em strategy.py encapsulam os diferentes algoritmos de avaliação, permitindo que sejam facilmente trocados.  
* **Observer**: O ResponseEvaluator (o "sujeito") notifica o ConsoleObserver assim que um resultado é calculado, permitindo que a interface seja atualizada de forma desacoplada.

## **Licença**

MIT