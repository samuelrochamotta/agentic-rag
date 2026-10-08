"""Testes offline do chunking e do DocumentStore (sem rede, sem API)."""

import numpy as np

from agentic_rag.ingest import CHUNK_OVERLAP, CHUNK_SIZE, chunk_pages
from agentic_rag.store import DocumentStore, find_headings, normalize, tokenize
from conftest import make_store


# -- tokenização ---------------------------------------------------------------

def test_tokenize_keeps_codes_whole_and_split():
    toks = tokenize("Erro ACX-7741 no sensor")
    assert "acx-7741" in toks
    assert "acx" in toks and "7741" in toks
    assert "erro" in toks


def test_tokenize_removes_accents():
    assert normalize("Política de Reembolso Ação") == "politica de reembolso acao"
    assert "politica" in tokenize("POLÍTICA")


# -- chunking ------------------------------------------------------------------

def _long_page(n_sentences: int = 40) -> str:
    return " ".join(f"Frase número {i} do texto de teste sobre o equipamento." for i in range(n_sentences))


def test_chunking_sizes_and_overlap():
    text = _long_page()
    chunks = chunk_pages("doc", [(1, text)])
    assert len(chunks) > 2
    for c in chunks:
        assert len(c.text) <= CHUNK_SIZE
        assert text[c.char_start:].startswith(c.text)  # offset bate com o texto da página
    for a, b in zip(chunks, chunks[1:]):
        a_end = a.char_start + len(a.text)
        overlap = a_end - b.char_start
        assert 0 < overlap <= CHUNK_OVERLAP + 5      # existe sobreposição, e não exagerada
        assert b.text.startswith("Frase")            # começa em início de frase
        assert a.text.endswith(".")                  # termina em fim de frase


def test_chunking_ids_pages_and_sections():
    pages = [
        (1, "1 Introdução\nTexto curto da introdução."),
        (2, "Continuação da introdução.\n2 Garantia\nA garantia é de 12 meses."),
        (3, _long_page()),  # sem cabeçalho: herda "2 Garantia"
    ]
    chunks = chunk_pages("manual", pages)
    assert chunks[0].id == "manual:p1:c0" and chunks[0].page == 1
    assert chunks[0].section == "1 Introdução"
    p2 = [c for c in chunks if c.page == 2]
    assert p2[0].section == "2 Garantia"  # cabeçalho aparece dentro do chunk
    p3 = [c for c in chunks if c.page == 3]
    assert [c.idx for c in p3] == list(range(len(p3)))
    assert all(c.id == f"manual:p3:c{c.idx}" for c in p3)
    assert all(c.section == "2 Garantia" for c in p3)
    # nenhum chunk mistura páginas
    assert all("Frase" not in c.text for c in chunks if c.page != 3)


def test_find_headings_ignores_table_rows():
    text = "4.2 Política de Reembolso\n3 unidades por caixa\n2024 foi um bom ano\n10 Anexos"
    titles = [t for _, t in find_headings(text)]
    assert titles == ["4.2 Política de Reembolso", "10 Anexos"]


# -- buscas --------------------------------------------------------------------

def test_bm25_finds_exact_code():
    store = make_store()
    hits = store.bm25_search("ACX-7741", k=3)
    assert hits[0][0].id == "manual:p1:c1"
    assert "ACX-7741" in hits[0][0].text
    # o código parecido (ACX-7714) não deve ganhar do exato
    assert all(score <= hits[0][1] for _, score in hits)


def test_bm25_accent_insensitive_and_uses_section():
    store = make_store()
    hits = store.bm25_search("politica reembolso", k=1)
    assert hits[0][0].id == "manual:p2:c2"


def test_bm25_no_match_returns_empty():
    assert make_store().bm25_search("inexistentezzz") == []


def test_vector_search_cosine():
    store = make_store()
    q = np.zeros(5, dtype=np.float32)
    q[3] = 2.0  # não normalizado de propósito
    hits = store.vector_search(q, k=2)
    assert hits[0][0].id == "manual:p2:c1"
    assert abs(hits[0][1] - 1.0) < 1e-6


def test_grep_finds_all_occurrences_without_duplicates():
    store = make_store()
    hits = store.grep(r"[A-Z]{3}-\d{4}")
    assert len(hits) == 3
    assert [c.page for c, _ in hits] == [1, 2, 2]
    assert "ACX-7741" in hits[0][1]
    # cada ocorrência é atribuída ao chunk certo via char_start
    assert hits[2][0].id == "manual:p2:c1" and "BRT-1002" in hits[2][1]


def test_grep_case_insensitive_and_invalid_regex():
    store = make_store()
    assert len(store.grep("acx-77")) == 2
    assert store.grep("(((") == []  # regex inválida vira literal, não explode
    assert len(store.grep("erro", max_hits=2)) == 2


# -- navegação -----------------------------------------------------------------

def test_get_chunk_and_neighbors():
    store = make_store()
    assert store.get_chunk("manual:p2:c0").page == 2
    assert store.get_chunk("nao:existe") is None
    ids = [c.id for c in store.neighbors("manual:p2:c0")]
    assert ids == ["manual:p1:c1", "manual:p2:c0", "manual:p2:c1"]  # atravessa a página
    assert [c.id for c in store.neighbors("manual:p1:c0", window=1)] == ["manual:p1:c0", "manual:p1:c1"]
    assert store.neighbors("nao:existe") == []


def test_get_page_outline_doc_ids():
    store = make_store()
    assert store.get_page("manual", 2).startswith("O erro ACX-7714")
    assert store.get_page("manual", 3) is None
    assert store.get_page("outro", 1) is None
    assert store.outline() == [
        {"doc_id": "manual", "page": 1, "section": "1 Introdução"},
        {"doc_id": "manual", "page": 1, "section": "2 Códigos de Erro"},
        {"doc_id": "manual", "page": 2, "section": "3 Política de Reembolso"},
    ]
    assert store.doc_ids() == ["manual"]


def test_save_and_load_roundtrip(tmp_path):
    store = make_store()
    store.save(tmp_path)
    loaded = DocumentStore.load(tmp_path)
    assert loaded.chunks == store.chunks
    assert np.allclose(loaded.embeddings, store.embeddings)
    assert loaded.pages == store.pages
    assert loaded.bm25_search("ACX-7741")[0][0].id == "manual:p1:c1"


def test_empty_store():
    store = DocumentStore.from_chunks([], np.zeros((0, 3), dtype=np.float32), {})
    assert store.bm25_search("x") == []
    assert store.vector_search(np.ones(3)) == []
    assert store.outline() == []
