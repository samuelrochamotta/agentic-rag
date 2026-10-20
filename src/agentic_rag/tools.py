"""Ferramentas do agente: os schemas (o "manual" que o LLM lê) e a execução em Python.

O LLM nunca vê este código Python — ele só vê `TOOL_SCHEMAS`: nome, descrição e
parâmetros de cada ferramenta. Por isso as descrições são a parte mais importante
deste arquivo: é lendo-as que o modelo decide QUAL busca usar para cada pergunta.
Uma descrição vaga ("busca no documento") faz o agente usar sempre a mesma
ferramenta; uma descrição que diz QUANDO usar cada uma faz ele escolher bem.
"""

import ast
import json
import operator

from .llm import LLMClient
from .store import Chunk, DocumentStore

MAX_OUTPUT_CHARS = 4000  # resultados longos enchem o contexto e encarecem cada passo seguinte
# read_page é a ferramenta de "ler a tabela inteira": cortá-la no meio esconde justamente a linha
# procurada. 12.000 cobre todas as páginas dos 84 relatórios do FinanceBench (a maior tem 10.436).
TOOL_OUTPUT_CHARS = {"read_page": 12000}
MAX_K = 20


def _fn(name: str, description: str, properties: dict, required: list[str]) -> dict:
    """Monta um schema no formato de tools da API da OpenAI."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


_K_PARAM = {"type": "integer", "description": "Quantos trechos devolver (padrão 5, máximo 20).", "default": 5}

TOOL_SCHEMAS: list[dict] = [
    _fn(
        "search_semantic",
        "Busca por SIGNIFICADO (embeddings). Encontra trechos que falam do mesmo assunto "
        "mesmo com outras palavras (paráfrases, sinônimos). Use para perguntas conceituais "
        "ou quando você não sabe os termos exatos usados no documento "
        "(ex.: 'como pedir o dinheiro de volta' acha a seção de reembolso). "
        "NÃO é boa para códigos, siglas, números ou nomes exatos — para isso use search_keyword.",
        {"query": {"type": "string", "description": "A pergunta ou descrição do que procura, em linguagem natural."},
         "k": _K_PARAM},
        ["query"],
    ),
    _fn(
        "search_keyword",
        "Busca por PALAVRAS EXATAS (BM25, ignora maiúsculas e acentos). Use para códigos "
        "(ex.: 'ACX-7741'), siglas, nomes próprios, números de seção, nomes de produtos ou "
        "termos técnicos específicos. Os trechos que contêm os termos mais raros da consulta "
        "vêm primeiro. Prefira consultas curtas só com os termos-chave, não frases inteiras. "
        "Devolve só os k melhores — para listar TODAS as ocorrências, use grep.",
        {"query": {"type": "string", "description": "Termos-chave, ex.: 'ACX-7741' ou 'garantia estendida'."},
         "k": _K_PARAM},
        ["query"],
    ),
    _fn(
        "grep",
        "Procura um padrão (regex, sem diferenciar maiúsculas) em TODO o texto e devolve "
        "TODAS as ocorrências, com o total, página e um trecho ao redor de cada uma. "
        "Use quando precisar CONTAR ou ENUMERAR (ex.: 'quantos/quais códigos de erro existem?' "
        "-> pattern 'ACX-\\d+'; 'todas as menções a prazo' -> 'prazo'). Não ranqueia por "
        "relevância. Um texto simples também funciona como padrão.",
        {"pattern": {"type": "string", "description": "Expressão regular ou texto literal, ex.: 'ACX-\\d{4}'."}},
        ["pattern"],
    ),
    _fn(
        "read_page",
        "Lê o texto COMPLETO de uma página. Use quando um trecho encontrado parece cortado, "
        "para ler TABELAS inteiras (as buscas devolvem só pedaços delas) ou quando precisar "
        "de todo o contexto de uma página. O doc_id é a parte antes de ':' no chunk_id "
        "(ex.: chunk_id 'manual:p3:c1' -> doc_id 'manual', page 3).",
        {"doc_id": {"type": "string", "description": "Identificador do documento."},
         "page": {"type": "integer", "description": "Número da página (começa em 1)."}},
        ["doc_id", "page"],
    ),
    _fn(
        "read_neighbors",
        "Devolve um trecho junto com os trechos imediatamente antes e depois dele (podendo "
        "atravessar a quebra de página). Use quando um resultado de busca parece incompleto: "
        "a frase continua no próximo trecho, uma lista foi cortada, ou falta a condição/exceção "
        "que vem logo em seguida.",
        {"chunk_id": {"type": "string", "description": "O chunk_id de um resultado anterior, ex.: 'manual:p3:c1'."},
         "window": {"type": "integer", "description": "Quantos trechos de cada lado (padrão 1).", "default": 1}},
        ["chunk_id"],
    ),
    _fn(
        "list_outline",
        "Mostra o SUMÁRIO do documento: todas as seções numeradas e a página onde cada uma "
        "começa. Use para se orientar no início, quando a pergunta cita uma seção pelo número "
        "ou nome (ex.: 'o que diz a seção 4.2?'), ou para descobrir onde um assunto deve estar.",
        {},
        [],
    ),
    _fn(
        "calculator",
        "Calcula uma expressão aritmética com precisão. Aceita números, + - * / ** %, e "
        "parênteses. Use SEMPRE que precisar somar, multiplicar, calcular percentuais, prazos "
        "ou diferenças com valores encontrados no documento — não faça contas de cabeça. "
        "Ex.: '1500 * 0.15' ou '(30 - 7) * 2'.",
        {"expression": {"type": "string", "description": "Expressão aritmética, ex.: '(1200 + 350) * 0.1'."}},
        ["expression"],
    ),
]


# ---------------------------------------------------------------------------
# Calculadora segura
# ---------------------------------------------------------------------------

# Nunca use eval() com texto vindo de um LLM: eval("__import__('os').system(...)")
# executaria qualquer coisa. Em vez disso, analisamos a expressão com `ast` e só
# aceitamos números e os operadores desta tabela — qualquer outro nó é rejeitado.
_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def safe_eval(expression: str) -> float | int:
    def ev(node: ast.AST):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left, right = ev(node.left), ev(node.right)
            # Sem limite, '9**9**9' travaria o processo calculando um número gigante.
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("expoente grande demais")
            return _BIN_OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"elemento não permitido: {type(node).__name__}")

    # Aceita vírgula decimal brasileira ("1,5") quando não há ponto na expressão.
    if "," in expression and "." not in expression:
        expression = expression.replace(",", ".")
    return ev(ast.parse(expression, mode="eval"))


# ---------------------------------------------------------------------------
# Execução das ferramentas
# ---------------------------------------------------------------------------

def _truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n...[truncado: {len(text) - limit} caracteres omitidos]"


def _chunk_dict(c: Chunk, **extra) -> dict:
    return {"chunk_id": c.id, "page": c.page, "section": c.section, **extra, "text": c.text}


def _to_json(items: list[dict]) -> str:
    """Um item por linha: JSON válido, mas fácil de ler (para o LLM e para quem depura)."""
    if not items:
        return "[]"
    return "[\n" + ",\n".join(json.dumps(it, ensure_ascii=False) for it in items) + "\n]"


class ToolBox:
    def __init__(self, store: DocumentStore, llm: LLMClient):
        self.store = store
        self.llm = llm
        # chunk_ids devolvidos por qualquer ferramenta, em ordem — útil para preencher
        # Answer.sources no agente.
        self.seen_chunks: list[str] = []

    def call(self, name: str, args: dict) -> str:
        """Executa a ferramenta `name`. Sempre devolve string; erros viram 'ERRO: ...'.

        Devolver o erro como texto (em vez de lançar exceção) deixa o próprio LLM
        ver o que deu errado e tentar de novo com outros argumentos.
        """
        if isinstance(args, str):  # tolera argumentos ainda em JSON bruto
            try:
                args = json.loads(args or "{}")
            except json.JSONDecodeError as e:
                return f"ERRO: argumentos não são JSON válido ({e})"
        method = getattr(self, f"_tool_{name}", None)
        if method is None:
            return f"ERRO: ferramenta desconhecida '{name}'. Disponíveis: " + ", ".join(
                t["function"]["name"] for t in TOOL_SCHEMAS)
        try:
            return _truncate(method(**(args or {})), TOOL_OUTPUT_CHARS.get(name, MAX_OUTPUT_CHARS))
        except TypeError as e:
            return f"ERRO: argumentos inválidos para {name}: {e}"
        except Exception as e:  # noqa: BLE001 — qualquer falha vira mensagem para o LLM
            return f"ERRO: {type(e).__name__}: {e}"

    def _remember(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            if c.id not in self.seen_chunks:
                self.seen_chunks.append(c.id)

    @staticmethod
    def _k(k) -> int:
        return max(1, min(int(k), MAX_K))

    # -- uma função por ferramenta -------------------------------------------

    def _tool_search_semantic(self, query: str, k: int = 5) -> str:
        query_vec = self.llm.embed([query])[0]
        hits = self.store.vector_search(query_vec, self._k(k))
        self._remember([c for c, _ in hits])
        return _to_json([_chunk_dict(c, score=round(s, 3)) for c, s in hits])

    def _tool_search_keyword(self, query: str, k: int = 5) -> str:
        hits = self.store.bm25_search(query, self._k(k))
        if not hits:
            return "Nenhum trecho contém esses termos. Tente sinônimos, search_semantic ou grep."
        self._remember([c for c, _ in hits])
        return _to_json([_chunk_dict(c, score=round(s, 2)) for c, s in hits])

    def _tool_grep(self, pattern: str) -> str:
        # Pedimos muitas ocorrências para poder informar o TOTAL, mesmo que só
        # algumas caibam na saída — contar é um dos usos principais do grep.
        hits = self.store.grep(pattern, max_hits=1000)
        if not hits:
            return f"Nenhuma ocorrência de /{pattern}/."
        self._remember([c for c, _ in hits])
        header = f"{len(hits)}{'+' if len(hits) >= 1000 else ''} ocorrência(s) de /{pattern}/:\n"
        items = [{"chunk_id": c.id, "page": c.page, "section": c.section, "text": snip} for c, snip in hits]
        return header + _to_json(items)

    def _tool_read_page(self, doc_id: str = "", page: int = 1) -> str:
        page = int(page)
        if doc_id not in self.store.pages and len(self.store.pages) == 1:
            doc_id = next(iter(self.store.pages))  # um só documento: não exige doc_id exato
        text = self.store.get_page(doc_id, page)
        if text is None:
            n = {d: len(p) for d, p in self.store.pages.items()}
            return f"ERRO: página {page} de '{doc_id}' não existe. Documentos (nº de páginas): {n}"
        self._remember([c for c in self.store.chunks if c.doc_id == doc_id and c.page == page])
        return f"[{doc_id} — página {page}]\n{text}"

    def _tool_read_neighbors(self, chunk_id: str, window: int = 1) -> str:
        chunks = self.store.neighbors(chunk_id, max(0, min(int(window), 5)))
        if not chunks:
            return f"ERRO: chunk_id '{chunk_id}' não existe."
        self._remember(chunks)
        return _to_json([_chunk_dict(c) for c in chunks])

    def _tool_list_outline(self) -> str:
        outline = self.store.outline()
        if not outline:
            return "Nenhuma seção numerada detectada no documento."
        return "\n".join(f"{o['doc_id']} p. {o['page']}: {o['section']}" for o in outline)

    def _tool_calculator(self, expression: str) -> str:
        try:
            result = safe_eval(expression)
        except ZeroDivisionError:
            return "ERRO: divisão por zero"
        except (SyntaxError, ValueError) as e:
            return f"ERRO: expressão inválida ({e}). Use só números, + - * / ** % e parênteses."
        if isinstance(result, float):
            result = round(result, 10)
            if result.is_integer():
                result = int(result)
        return f"{expression} = {result}"
