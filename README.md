# agentic-rag

Projeto didático para comparar dois jeitos de fazer RAG (Retrieval-Augmented Generation)
sobre o mesmo PDF:

- **RAG simples**: gera o embedding da pergunta, pega os 5 chunks mais parecidos e faz **uma** chamada ao LLM.
- **RAG agêntico**: o LLM recebe um conjunto de **ferramentas de busca** e decide sozinho, em vários
  passos, o que procurar, como procurar e quando já tem evidência suficiente para responder.

Os dois usam o mesmo modelo de chat, o mesmo modelo de embedding, os mesmos chunks e `temperature=0`.
Só a estratégia de recuperação muda. Os modelos rodam via [OpenRouter](https://openrouter.ai).

## Resultado num benchmark externo: FinanceBench

[FinanceBench](https://github.com/patronus-ai/financebench): as 150 perguntas abertas sobre 84
relatórios da SEC em PDF (10-K, 10-Q, 8-K), com gabarito humano. Um índice por documento, como
na configuração *single store* do artigo original. Chat `deepseek/deepseek-v4.1-flash`, juiz
`openai/gpt-6-luna` (outro modelo), embeddings `openai/text-embedding-3-small`.

| sistema | acurácia | recall de evidência | US$/pergunta | latência média |
|---|--:|--:|--:|--:|
| RAG simples | 56,7% (1 rodada) | 69% | 0,0013 | 1 chamada (latência medida com fila: não confiável) |
| RAG agêntico | **88,0%** (3 rodadas: 87,3–89,3%) | 93–95% | 0,0025 | ~14 s |

**Meta não atingida:** o alvo era ≥ 90%. Ficamos ~2 pontos abaixo, e abaixo do topo da lista
comunitária citada a seguir.

Referências publicadas, não diretamente comparáveis (outros modelos, juízes e configurações):
GPT-4-Turbo com índice compartilhado ~19%; com o documento inteiro no contexto ~79%; recebendo a
passagem certa ("oráculo") 85%. O topo de uma
[lista comunitária](https://benchmarklist.com/benchmarks/financebench/) está em 89,33%.

**Como ler:**
- *Recall de evidência* = a página anotada pelos autores está entre as que o sistema viu. O agêntico
  vê a evidência em ~94% das perguntas; a maior parte dos erros restantes é de interpretação.
- Dos 15 erros persistentes, a maioria diverge do gabarito na *definição* do índice (quick ratio,
  capital de giro "operacional", giro de estoque) ou num julgamento ("é intensivo em capital?").
  Não ajustamos o sistema a esses casos.
- **Atenção: as mesmas 150 perguntas serviram para analisar os erros e para medir** (não há outra
  divisão aberta). Duas mudanças entraram depois dessa análise: o `read_page` deixou de cortar em
  4.000 caracteres (36% das páginas de 10-K passavam disso) e `ANSWER_RULES` ganhou a regra de
  calcular indicadores com a definição usual e concluir. Os exemplos dessa regra ("é intensivo em
  capital?") e a nota sobre parênteses negativos foram tirados de erros do próprio benchmark. É
  ajuste no conjunto de teste, mesmo com mecanismo geral.
- Antes delas: 84,7% (1 rodada). O ganho de ~3 pontos é da ordem da variação entre rodadas (2
  pontos). O conserto do corte resolveu 2 dos 5 erros com página truncada; o resto veio do prompt.
  Parte da instabilidade (7 perguntas oscilam entre rodadas) vem do próprio juiz, que também não é
  determinístico.
- No conjunto interno (42 perguntas, mesmo chat e juiz), o agêntico fez 99–100% em 3 rodadas antes
  das mudanças e 100% em 1 rodada depois; o simples, 71–76%. Esse conjunto já não separa versões do
  sistema: ele serve de guarda contra regressão.

Rode com `uv run rag financebench --systems simple,agentic` (veja `eval/README.md`).

## Rodada original (18 perguntas, `openai/gpt-4.1-mini`)

| categoria | simples | agêntico |
|---|:-:|:-:|
| simples (controle) | 2/2 | 2/2 |
| multi_hop | 2/3 | 3/3 |
| codigo_exato | 2/3 | 3/3 |
| agregacao | 1/3 | 2/3 |
| distrator | 3/3 | 3/3 |
| referencia_secao | 0/2 | 2/2 |
| sem_resposta | 2/2 | 2/2 |
| **total** | **67%** | **94%** |
| chamadas LLM por pergunta | 1,0 | 2,7 |
| tokens por pergunta | ~1.150 | ~6.060 |
| custo das 18 perguntas | US$ 0,009 | US$ 0,031 |
| latência média | 2,6 s | 4,7 s |

Detalhes por pergunta, com o motivo de cada erro, em [`eval/results.md`](eval/results.md).
As respostas completas e o trace do agente estão em `eval/results.json`.

O conjunto atual tem **42 perguntas**, incluindo 24 adicionais com cálculos, exceções,
cadeias de busca e informação parcialmente ausente. A tabela acima registra a rodada
original de 18 perguntas. Veja os casos difíceis e os comandos de comparação entre
simples, agêntico e híbrido em [`eval/README.md`](eval/README.md).

**Como ler esses números:**
- O agêntico acertou mais, mas custou cerca de **3,3×** mais e levou quase o dobro do tempo.
- O ganho está onde o top-k vetorial é estruturalmente fraco:
  - "o que diz a seção 7.3?": o embedding da pergunta não se parece com o texto da seção;
  - códigos quase idênticos (ACX-7741 vs ACX-7714);
  - perguntas que exigem juntar duas páginas.
- Nas perguntas diretas e nos distratores (versão vigente vs revogada de uma política) os dois empatam.
- O agente também erra. Na q09 ele fez uma única busca, somou 11 em vez de 12 e não usou o `grep`
  para enumerar todas as ocorrências. Agentes economizam esforço quando acham que já têm a resposta.
- São 18 perguntas e uma rodada só. LLMs variam entre execuções, então rode `rag eval` mais de uma vez
  antes de tirar conclusões fortes.

## Como funciona

```
                RAG SIMPLES                                RAG AGÊNTICO
  pergunta ─► embedding ─► top-5 chunks          pergunta ─► LLM ◄─────────────┐
                              │                               │ decide        │
                              ▼                               ▼               │
                     LLM responde (1 chamada)      tool_call: search_keyword, │
                                                   grep, read_page, ...       │
                                                              │               │
                                                              ▼               │
                                                   executa a ferramenta ──────┘
                                                   (repete até ter evidência,
                                                    no máximo 8 passos)
                                                              │
                                                              ▼
                                                      resposta com [p. N]
```

O loop agêntico (`src/agentic_rag/agent.py`) é escrito à mão, sem framework, para você ver cada etapa:
1. **pensar**: o LLM recebe o histórico e a lista de ferramentas;
2. **agir**: se ele devolve `tool_calls`, executamos cada uma;
3. **observar**: os resultados voltam como mensagens `role="tool"`, e o ciclo recomeça.

Quando o LLM responde sem chamar ferramenta, o loop termina.

### Ferramentas do agente (`src/agentic_rag/tools.py`)

| ferramenta | quando usar | por que existe |
|---|---|---|
| `search_semantic` | paráfrases, perguntas conceituais | busca por significado (embeddings + cosseno) |
| `search_keyword` | códigos, siglas, nomes próprios | BM25: casa termos exatos que o embedding "borra" (ACX-7741 ≈ ACX-7714) |
| `grep` | contar ou enumerar **todas** as ocorrências | busca exaustiva; o top-k sempre corta resultados |
| `read_page` | tabelas, "o que tem na página 9" | contexto completo, sem cortes de chunk |
| `read_neighbors` | o trecho achado parece cortado | expande o chunk para os vizinhos |
| `list_outline` | a pergunta cita seção ou página | sumário (seções → páginas) |
| `calculator` | somas, médias | LLMs erram aritmética; a calculadora usa `ast`, sem `eval` |

As descrições dessas ferramentas são o "manual" que o LLM lê para escolher qual chamar. Vale a pena
ler `TOOL_SCHEMAS` e o system prompt em `agent.py`.

### Pipeline de ingestão (`src/agentic_rag/ingest.py`, `store.py`)

1. O `pypdf` extrai o texto página a página.
2. Cada página vira chunks de ~800 caracteres, com 150 de sobreposição e quebra em fim de frase. Cada
   chunk guarda a página e a seção (cabeçalho numerado como `4.2 Título`).
3. Os embeddings são gerados em lote e normalizados, então produto escalar = cosseno.
4. Tudo é salvo em `.index/<hash>/`. O hash depende do PDF, do modelo e dos parâmetros de chunking,
   então reingerir o mesmo arquivo não gasta nada.

### Modo híbrido: decisões tipadas (`src/agentic_rag/hybrid.py`, `decider.py`)

Experimento para gastar o agente só onde ele faz diferença. Algumas decisões da arquitetura são
**fechadas** ("essa pergunta é simples?", "a evidência já basta?"). Para elas não precisamos de texto
livre: precisamos de uma resposta de tipo conhecido e de uma confiança para comparar com um limiar.

```
pergunta ─► ROTEADOR (escolha entre 5 tipos) ──"simples" e confiança ≥ ROUTE_THRESHOLD──► RAG simples
                   │
                   └─ qualquer outro caso ─► RAG agêntico + dica da 1ª ferramenta
                                             (agregacao → grep, referencia_secao → list_outline, ...)
                                                   │
                                quando o agente quer parar: VERIFICADOR (sim/não)
                                "as evidências sustentam toda a resposta?"
                                P(sim) < EVIDENCE_THRESHOLD → busca mais uma vez (no máximo uma)
```

Quem decide é um `Decider`, com duas implementações:

- **`jev`** (padrão): o [Jev, da TypeSafe AI](https://docs.typesafe.ai/api), servido pelo OpenRouter
  com a mesma chave. Não é um LLM: recebe um estado e perguntas tipadas e devolve as respostas numa
  passada só, com probabilidade por opção. Por isso não usa chat completions: a chamada é HTTP puro
  para `POST https://openrouter.ai/api/v1/systemone`, para ficar visível o que vai e o que volta.
- **`llm`**: o próprio `CHAT_MODEL` com saída estruturada (JSON schema). É a linha de base: sem ela
  não dá para saber se o Jev ajuda ou se qualquer saída estruturada já bastaria. A confiança aqui é
  autodeclarada pelo modelo, o que costuma ser mal calibrado.

Limitações:

- O roteador só vê a pergunta, não o documento. Ele classifica pela forma da pergunta; `distrator` e
  `sem_resposta` dependem do conteúdo e não entram na classificação. Na dúvida, a pergunta vai para o
  agente.
- O verificador não roda quando o rascunho diz "não encontrei": nesse caso ele responderia "não" sempre.
- O custo do Jev vem do campo `usage.cost` que o OpenRouter devolve. Se ele faltar, o relatório avisa
  que o custo do híbrido está subestimado. As chamadas ao Jev aparecem na coluna "decisões", não em
  "chamadas LLM".
- Ainda não há números do híbrido neste README: rode `rag eval` e compare.

## Como rodar

Requer [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env            # coloque sua OPENROUTER_API_KEY
uv sync

uv run python data/gerar_pdf.py # (re)gera o PDF simulado em data/
uv run rag ingest data/manual_simulado.pdf

uv run rag ask "Quem gerencia o CD onde houve o vazamento de amônia?" --mode both --verbose
uv run rag chat --mode agentic  # REPL interativo (cada pergunta é independente)
uv run rag ask "Quantos incidentes classe 3 houve em 2024?" --mode hybrid --verbose
uv run rag eval                 # roda as 42 perguntas nos três modos e gera eval/results.md
uv run rag eval --systems hybrid --decider llm   # só o híbrido, com o LLM decidindo
uv run pytest -q                # testes offline (sem rede)
```

`--verbose` mostra o trace do agente: cada ferramenta chamada, os argumentos e um resumo do resultado.
Os modelos podem ser trocados no `.env` (`CHAT_MODEL`, `EMBED_MODEL`).
O modo híbrido usa o Jev pelo OpenRouter (`JEV_MODEL`, padrão `jev-latest`); `--decider llm` troca
pelo próprio `CHAT_MODEL`.

## Avaliação

- O PDF (`data/gerar_pdf.py`) é um manual fictício de 16 páginas, escrito para expor as fraquezas
  conhecidas do RAG simples: multi-hop, códigos quase idênticos, agregação espalhada pelo documento,
  distratores, referência a seção e perguntas sem resposta. Veja [`eval/README.md`](eval/README.md).
- Uma resposta só conta como correta quando passa nas duas checagens:
  - **determinística**: os termos de `must_contain` aparecem na resposta, sem diferenciar
    maiúsculas nem acentos;
  - **juiz LLM**: compara a resposta com o gabarito.
- Nas perguntas `sem_resposta`, o sistema precisa declarar que não encontrou a informação.
- O custo do juiz não entra na conta dos sistemas.

## Estrutura

```
src/agentic_rag/
  config.py      # .env → Settings
  llm.py         # cliente OpenRouter + contabilização de uso (tokens, US$, latência)
  ingest.py      # PDF → chunks → embeddings → índice em disco
  store.py       # BM25, busca vetorial, grep, páginas, sumário
  tools.py       # ferramentas do agente (schemas + implementação)
  prompts.py     # instruções compartilhadas pelos dois RAGs
  agent.py       # loop agêntico
  simple_rag.py  # baseline
  decider.py     # decisões tipadas: Jev (TypeSafe) ou LLM com JSON schema
  hybrid.py      # roteador + verificador em volta dos dois RAGs
  evaluate.py    # avaliação comparativa
  cli.py         # comando `rag`
data/gerar_pdf.py
eval/questions.json
tests/
SPEC.md          # contrato interno entre os módulos
```

## Ideias para experimentar

- Dar ao RAG simples busca híbrida (BM25 + vetorial) ou rerank, e ver quanto da diferença some.
- Trocar o `CHAT_MODEL` por um modelo mais fraco ou mais forte. Agentes dependem muito da qualidade
  do tool calling.
- Reduzir `--max-steps` e observar o trade-off entre custo e acurácia.
- Criar perguntas novas em `eval/questions.json`, ou apontar o projeto para um PDF seu.
