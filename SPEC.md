# SPEC — contrato interno entre os módulos

Projeto didático: comparar **RAG simples** (embed → top-k → responde) com **RAG agêntico**
(LLM com ferramentas decide como buscar, em várias rodadas). Código e comentários em português,
legível acima de abstrato. Python 3.12, gerenciado com `uv` (`uv run ...`).

## Regras de comparação justa
- Mesmo modelo de chat (`CHAT_MODEL`), mesmo modelo de embedding (`EMBED_MODEL`), mesmos chunks, `temperature=0`.
- Só muda a estratégia de recuperação.
- Ambos devolvem `Answer` com métricas de custo (chamadas, tokens, US$, latência).

## Layout
```
src/agentic_rag/
  config.py      # (pronto) Settings via .env
  llm.py         # (pronto) LLMClient: chat(), embed(), Usage
  ingest.py      # PDF -> páginas -> chunks -> embeddings -> índice em disco (.index/<hash>/)
  store.py       # DocumentStore: BM25, vetorial, get_chunk, neighbors, get_page, outline
  tools.py       # ferramentas do agente: schemas JSON + funções Python
  agent.py       # loop agêntico com tool calling
  simple_rag.py  # baseline
  evaluate.py    # roda as perguntas de eval/questions.json nos dois modos e gera eval/results.md
  cli.py         # entrypoint `rag`
data/gerar_pdf.py  # gera data/manual_simulado.pdf
eval/questions.json
tests/
```

## Tipos (em `store.py`)
```python
@dataclass
class Chunk:
    id: str          # f"{doc_id}:p{page}:c{idx}"  ex.: "manual_simulado:p3:c1"
    doc_id: str      # nome do arquivo sem extensão
    page: int        # 1-based
    idx: int         # índice do chunk dentro da página (0-based)
    text: str
    section: str | None = None   # título de seção detectado (ex.: "4.2 Política de Reembolso"), se houver
```

Chunking: por página, em janelas de ~800 caracteres com sobreposição de ~150, quebrando em limite de
parágrafo/frase quando possível. Detectar o último cabeçalho numerado visto (regex `^\d+(\.\d+)*\s+\S`)
e gravar em `section`.

## `ingest.py`
- `load_pdf(path) -> list[tuple[int, str]]` (página 1-based, texto) via pypdf.
- `chunk_pages(doc_id, pages) -> list[Chunk]`.
- `build_index(pdf_paths: list[Path], llm: LLMClient, index_dir: Path = Path(".index")) -> Path`
  - Índice identificado por hash sha256 do conteúdo dos PDFs; se já existe, reaproveita (não re-embeda).
  - Grava `chunks.json`, `embeddings.npy` (float32, normalizados L2), `pages.json` (doc_id -> lista de textos).
  - Embeddings em lote (até 100 textos por chamada).

## `store.py` — `DocumentStore`
```python
class DocumentStore:
    @classmethod
    def load(cls, index_path: Path) -> "DocumentStore"
    chunks: list[Chunk]
    def bm25_search(self, query: str, k: int = 5) -> list[tuple[Chunk, float]]
    def vector_search(self, query_vec: np.ndarray, k: int = 5) -> list[tuple[Chunk, float]]   # cosseno
    def grep(self, pattern: str, max_hits: int = 20) -> list[tuple[Chunk, str]]   # regex case-insensitive; devolve trecho ao redor
    def get_chunk(self, chunk_id: str) -> Chunk | None
    def neighbors(self, chunk_id: str, window: int = 1) -> list[Chunk]
    def get_page(self, doc_id: str, page: int) -> str | None
    def outline(self) -> list[dict]   # [{doc_id, page, section}] seções únicas em ordem
    def doc_ids(self) -> list[str]
```
Tokenização do BM25: minúsculas, remove acentos (unicodedata NFKD), split em `\w+`, mantém tokens
alfanuméricos como `ACX-7741` também inteiros (ex.: além de `acx`, `7741`, indexar `acx-7741`).

## `tools.py`
```python
TOOL_SCHEMAS: list[dict]   # formato OpenAI tools
class ToolBox:
    def __init__(self, store: DocumentStore, llm: LLMClient)
    def call(self, name: str, args: dict) -> str     # sempre devolve string (JSON ou texto); erros viram string "ERRO: ..."
```
Ferramentas (cada resultado lista `chunk_id`, `page`, `section` e texto):
| nome | args | para quê |
|---|---|---|
| `search_semantic` | query, k=5 | similaridade por significado (paráfrases) |
| `search_keyword` | query, k=5 | BM25 — termos/códigos exatos, siglas, nomes |
| `grep` | pattern | regex literal em todo o texto — contagens, enumerar todas as ocorrências |
| `read_page` | doc_id, page | ler página inteira (tabelas, contexto completo) |
| `read_neighbors` | chunk_id, window=1 | expandir contexto de um chunk |
| `list_outline` | — | sumário: seções e páginas |
| `calculator` | expression | aritmética segura (ast; só números e + - * / ** % parênteses) |

Saída de tool truncada em ~4000 caracteres.

## `agent.py`
```python
def run_agent(question: str, store, llm, max_steps: int = 8, verbose: bool = False, console=None,
              toolbox=None, tool_schemas=None, extra_instructions: str | None = None,
              check_final: Callable[[str, list[dict]], str | None] | None = None) -> Answer
```
Loop: system prompt (pt-BR) instrui a planejar, usar ferramentas, citar páginas `[p. N]`, e dizer
explicitamente "Não encontrei essa informação no documento" quando não houver evidência.
Em cada passo: chama `llm.chat(messages, tools=TOOL_SCHEMAS)`; se houver tool_calls, executa todos, anexa
resultados e continua; senão termina. Ao atingir `max_steps`, força resposta final sem tools.
`verbose=True` imprime trace com rich (passo, tool, args, resumo do resultado).
`extra_instructions` é anexado ao system prompt. `check_final(rascunho, mensagens)` roda quando o modelo
quer parar (no máximo uma vez, só se ainda houver passos); se devolver texto, ele volta como mensagem
`user` e o loop continua.

## `decider.py` e `hybrid.py`
```python
class Decider(Protocol):
    name: str
    def decide(self, state: str | dict, questions: dict[str, Choice | Noul], llm) -> dict[str, Decision]
def run_hybrid(question: str, store, llm, decider: Decider, max_steps: int = 8, ...) -> Answer
```
`Decision(value, confidence, probabilities)`. Implementações: `JevDecider` (HTTP para
`<OPENROUTER_BASE_URL>/systemone`) e `LLMDecider` (chat com JSON schema). O decider registra o uso em
`llm.usage` (`decider_calls`, latência e custo; o do Jev vem em `usage.cost` do OpenRouter).
`run_hybrid`: roteador (Choice) → `run_simple` se "simples" com confiança ≥ `ROUTE_THRESHOLD`, senão
`run_agent` com dica e verificador de evidência (Noul). `trace[0]` registra a rota.

## `simple_rag.py`
```python
def run_simple(question: str, store, llm, k: int = 5) -> Answer
```
Embeda a pergunta → `vector_search` top-k → uma única chamada de chat com os chunks no prompt. Nada mais
(nada de híbrido, rerank ou reescrita de query). Mesmo texto de instrução sobre citar páginas e dizer
"Não encontrei...".

## `Answer` (em `llm.py`)
```python
@dataclass
class Answer:
    text: str
    sources: list[str]            # chunk_ids usados
    usage: Usage                  # chamadas, decisões, tokens, custo, latência
    trace: list[dict] = field(default_factory=list)   # passos do agente (vazio no simples)
```

## `eval/questions.json`
```json
[{"id": "q01", "category": "multi_hop|codigo_exato|agregacao|distrator|sem_resposta|referencia_secao|simples",
  "question": "...", "gold": "resposta de referência",
  "must_contain": ["termos que DEVEM aparecer na resposta (opcional; checagem determinística, case/acento-insensitive)"]}]
```

## `evaluate.py`
- Para cada pergunta roda `run_simple` e `run_agent`.
- Nota: se `must_contain` não vazio → todos presentes = correto; **além disso** LLM-as-judge (mesmo
  `CHAT_MODEL`, temperature 0) compara com `gold` e devolve JSON `{"correct": bool, "reason": str}`.
  Correto final = juiz diz correto E (must_contain vazio OU todos presentes).
  Para `sem_resposta`, correto = resposta declara que a informação não está no documento.
- Saída: tabela rich no terminal + `eval/results.md` (por pergunta e agregado por categoria: acurácia,
  chamadas LLM, tokens, custo US$, latência média) + `eval/results.json`.

## `cli.py` (comando `rag`)
```
rag ingest data/manual_simulado.pdf          # constrói índice
rag ask "pergunta" [--mode agentic|simple|both] [--verbose]
rag chat [--mode agentic|simple]             # REPL interativo
rag eval [--only q01,q02]                    # roda avaliação
```
O índice ativo fica registrado em `.index/current` (caminho do último índice construído).
