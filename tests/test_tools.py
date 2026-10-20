"""Testes offline das ferramentas do agente (LLM falso, sem rede)."""

import json

import numpy as np
import pytest

from agentic_rag.tools import TOOL_OUTPUT_CHARS, TOOL_SCHEMAS, ToolBox, safe_eval
from conftest import make_store


class FakeLLM:
    """Só precisa de `embed`. Mapeia palavras para eixos dos embeddings one-hot do store."""

    AXES = {"sensor": 1, "superaquecimento": 2, "devolucao": 4}

    def __init__(self):
        self.embed_calls = 0

    def embed(self, texts):
        self.embed_calls += 1
        out = np.zeros((len(texts), 5), dtype=np.float32)
        for i, t in enumerate(texts):
            for word, axis in self.AXES.items():
                if word in t.lower():
                    out[i, axis] = 1.0
        return out


@pytest.fixture
def box():
    return ToolBox(make_store(), FakeLLM())


def test_schemas_match_spec():
    names = [t["function"]["name"] for t in TOOL_SCHEMAS]
    assert names == ["search_semantic", "search_keyword", "grep", "read_page",
                     "read_neighbors", "list_outline", "calculator"]
    for t in TOOL_SCHEMAS:
        assert t["type"] == "function"
        fn = t["function"]
        assert len(fn["description"]) > 80  # descrições precisam ser um "manual" de verdade
        assert fn["parameters"]["type"] == "object"
        assert set(fn["parameters"]["required"]) <= set(fn["parameters"]["properties"])


def test_search_semantic_uses_embed(box):
    out = json.loads(box.call("search_semantic", {"query": "pedido de devolucao", "k": 1}))
    assert out[0]["chunk_id"] == "manual:p2:c2"
    assert set(out[0]) >= {"chunk_id", "page", "section", "text"}
    assert box.llm.embed_calls == 1


def test_search_keyword_exact_code(box):
    out = json.loads(box.call("search_keyword", {"query": "ACX-7741"}))
    assert out[0]["chunk_id"] == "manual:p1:c1"
    assert out[0]["page"] == 1 and out[0]["section"] == "2 Códigos de Erro"
    assert "manual:p1:c1" in box.seen_chunks


def test_search_keyword_no_hits_is_text(box):
    assert "Nenhum trecho" in box.call("search_keyword", {"query": "zzzz"})


def test_grep_reports_total(box):
    out = box.call("grep", {"pattern": r"[A-Z]{3}-\d{4}"})
    assert out.startswith("3 ocorrência(s)")
    items = json.loads(out.split("\n", 1)[1])
    assert [i["page"] for i in items] == [1, 2, 2]


def test_read_page_and_neighbors(box):
    out = box.call("read_page", {"doc_id": "manual", "page": 2})
    assert "BRT-1002" in out and "página 2" in out
    assert box.call("read_page", {"doc_id": "manual", "page": 9}).startswith("ERRO")
    # com um só documento, doc_id errado é tolerado
    assert "BRT-1002" in box.call("read_page", {"doc_id": "manual_simulado", "page": 2})
    nb = json.loads(box.call("read_neighbors", {"chunk_id": "manual:p2:c0"}))
    assert [n["chunk_id"] for n in nb] == ["manual:p1:c1", "manual:p2:c0", "manual:p2:c1"]
    assert box.call("read_neighbors", {"chunk_id": "x"}).startswith("ERRO")


def test_list_outline(box):
    out = box.call("list_outline", {})
    assert "manual p. 2: 3 Política de Reembolso" in out


def test_calculator(box):
    assert box.call("calculator", {"expression": "(1200 + 300) * 0.1"}) == "(1200 + 300) * 0.1 = 150"
    assert box.call("calculator", {"expression": "7 / 2"}).endswith("= 3.5")
    assert box.call("calculator", {"expression": "-2 ** 2 % 3"}).startswith("-2 ** 2 % 3 =")
    assert box.call("calculator", {"expression": "1,5 * 2"}).endswith("= 3")
    assert box.call("calculator", {"expression": "1/0"}) == "ERRO: divisão por zero"


@pytest.mark.parametrize("expr", [
    "__import__('os').system('echo pwned')",
    "open('/etc/passwd').read()",
    "().__class__",
    "a + 1",
    "9 ** 9 ** 9",
    "[1, 2]",
    "'abc' * 3",
])
def test_calculator_rejects_unsafe(box, expr):
    assert box.call("calculator", {"expression": expr}).startswith("ERRO")
    with pytest.raises((ValueError, SyntaxError)):
        safe_eval(expr)


def test_errors_become_strings(box):
    assert box.call("nao_existe", {}).startswith("ERRO: ferramenta desconhecida")
    assert box.call("search_keyword", {}).startswith("ERRO")          # falta query
    assert box.call("read_page", {"doc_id": "manual", "page": "abc"}).startswith("ERRO")
    # argumentos em JSON bruto (como vêm da API) também funcionam
    assert "ACX-7741" in box.call("search_keyword", '{"query": "ACX-7741"}')


def test_output_is_truncated(box):
    # read_page tem limite próprio, maior: uma página de 10 mil caracteres passa inteira...
    box.store.pages["manual"][0] = "x" * 10_000
    assert "truncado" not in box.call("read_page", {"doc_id": "manual", "page": 1})
    # ...mas acima do limite dela também é cortada.
    box.store.pages["manual"][0] = "x" * 20_000
    out = box.call("read_page", {"doc_id": "manual", "page": 1})
    assert len(out) < TOOL_OUTPUT_CHARS["read_page"] + 100
    assert "truncado" in out
