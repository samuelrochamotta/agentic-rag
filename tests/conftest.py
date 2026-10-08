"""Dados sintéticos compartilhados pelos testes (sem rede, sem API)."""

import numpy as np

from agentic_rag.store import Chunk, DocumentStore


def make_store() -> DocumentStore:
    """Store sintético: 2 páginas, 5 chunks, embeddings 'one-hot' falsos."""
    pages = {
        "manual": [
            "1 Introdução\nEste manual descreve o equipamento.\n"
            "2 Códigos de Erro\nO erro ACX-7741 indica falha no sensor.",
            "O erro ACX-7714 indica superaquecimento. O erro BRT-1002 indica bateria fraca.\n"
            "3 Política de Reembolso\nO reembolso é feito em até 30 dias.",
        ]
    }
    # (página, início do chunk no texto da página, seção) — os chunks vão de um início ao próximo
    p1, p2 = pages["manual"]
    layout = [
        (1, 0, "1 Introdução"),
        (1, p1.index("2 Códigos"), "2 Códigos de Erro"),
        (2, 0, "2 Códigos de Erro"),
        (2, p2.index("O erro BRT"), "2 Códigos de Erro"),
        (2, p2.index("3 Política"), "3 Política de Reembolso"),
    ]
    chunks = []
    for n, (pg, start, section) in enumerate(layout):
        page_text = pages["manual"][pg - 1]
        end = layout[n + 1][1] if n + 1 < len(layout) and layout[n + 1][0] == pg else len(page_text)
        idx = sum(1 for c in chunks if c.page == pg)
        chunks.append(Chunk(id=f"manual:p{pg}:c{idx}", doc_id="manual", page=pg, idx=idx,
                            text=page_text[start:end].strip(), section=section, char_start=start))
    embeddings = np.eye(len(chunks), dtype=np.float32)  # chunk i "aponta" para o eixo i
    return DocumentStore.from_chunks(chunks, embeddings, pages)
