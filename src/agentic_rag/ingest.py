"""Ingestão: PDF -> páginas -> chunks -> embeddings -> índice em disco.

Esta etapa roda uma vez por documento. Tanto o RAG simples quanto o agêntico
usam exatamente o mesmo índice — a comparação entre eles só é justa assim.
"""

import hashlib
import shutil
from pathlib import Path

from pypdf import PdfReader

from .llm import LLMClient
from .store import Chunk, DocumentStore, find_headings

CHUNK_SIZE = 800     # caracteres por chunk (alvo)
CHUNK_OVERLAP = 150  # caracteres repetidos entre chunks vizinhos


def load_pdf(path: Path) -> list[tuple[int, str]]:
    """Extrai o texto de cada página: [(1, "texto da p. 1"), (2, ...), ...]."""
    reader = PdfReader(str(path))
    return [(i, page.extract_text() or "") for i, page in enumerate(reader.pages, start=1)]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _best_break(text: str, start: int, end: int) -> int:
    """Escolhe onde cortar o chunk que vai de `start` até no máximo `end`.

    Preferimos cortar num fim de parágrafo, depois num fim de frase, depois num
    espaço — nessa ordem. Cortar no meio de uma frase gera chunks que "começam do
    nada", o que piora tanto o embedding quanto a leitura pelo LLM. Só procuramos
    na segunda metade da janela para não gerar chunks minúsculos.
    """
    floor = start + (end - start) // 2
    for sep in ("\n\n", ". ", "? ", "! ", ".\n", "\n", " "):
        pos = text.rfind(sep, floor, end)
        if pos != -1:
            return pos + len(sep)
    return end  # sem nenhum separador: corta seco


def _overlap_start(text: str, end: int, overlap: int) -> int:
    """Onde começa o próximo chunk: ~`overlap` caracteres antes do fim do atual.

    A sobreposição existe para que uma informação que caia bem na fronteira entre
    dois chunks apareça inteira em pelo menos um deles. Ajustamos o início para um
    começo de frase (ou ao menos de palavra) dentro da região de sobreposição.
    """
    lo = max(0, end - overlap)
    hi = end - overlap // 3  # garante uma sobreposição mínima de ~1/3 do alvo
    for sep in (". ", "\n"):
        pos = text.find(sep, lo, hi)
        if pos != -1:
            return pos + len(sep)
    pos = text.find(" ", lo, hi)
    return pos + 1 if pos != -1 else lo


def _split_page(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[tuple[int, int]]:
    """Divide o texto de uma página em janelas (início, fim) sobrepostas."""
    spans = []
    start, n = 0, len(text)
    while start < n:
        end = n if n - start <= size else _best_break(text, start, start + size)
        spans.append((start, end))
        if end >= n:
            break
        nxt = _overlap_start(text, end, overlap)
        start = nxt if nxt > start else end  # garante que sempre avançamos
    return spans


def chunk_pages(doc_id: str, pages: list[tuple[int, str]]) -> list[Chunk]:
    """Transforma páginas em chunks, um documento por vez.

    - Nunca juntamos texto de páginas diferentes num chunk: assim cada chunk tem
      UMA página, e a citação "[p. N]" é sempre exata.
    - `section` = último cabeçalho numerado visto até o fim do chunk. Ele é
      "herdado" entre páginas: se a seção 4.2 começa na p. 5 e continua na p. 6,
      os chunks da p. 6 também são da seção 4.2.
    """
    chunks: list[Chunk] = []
    current_section: str | None = None
    for page_num, text in pages:
        headings = find_headings(text)
        idx = 0
        for start, end in _split_page(text):
            chunk_text = text[start:end].strip()
            # Atualiza a seção com qualquer cabeçalho que apareça antes do fim deste chunk.
            for pos, title in headings:
                if pos < end:
                    current_section = title
            if not chunk_text:
                continue
            chunks.append(Chunk(
                id=f"{doc_id}:p{page_num}:c{idx}", doc_id=doc_id, page=page_num, idx=idx,
                text=chunk_text, section=current_section, char_start=start,
            ))
            idx += 1
    return chunks


# ---------------------------------------------------------------------------
# Índice em disco
# ---------------------------------------------------------------------------

def _index_hash(pdf_paths: list[Path], embed_model: str) -> str:
    """Identidade do índice: conteúdo dos PDFs + modelo de embedding + parâmetros de chunking.

    Se qualquer um desses mudar, os embeddings antigos não servem mais — então o
    hash muda e um índice novo é criado. Se nada mudou, reaproveitamos o antigo
    e não pagamos de novo pelos embeddings.
    """
    h = hashlib.sha256()
    for p in pdf_paths:
        h.update(p.read_bytes())
    h.update(f"|{embed_model}|{CHUNK_SIZE}|{CHUNK_OVERLAP}".encode())
    return h.hexdigest()[:16]


def _embedding_text(c: Chunk) -> str:
    # O título da seção entra no texto embedado: um chunk do meio da seção
    # "4.2 Política de Reembolso" fica semanticamente ligado a "reembolso"
    # mesmo que a palavra não apareça nele.
    return f"{c.section}\n{c.text}" if c.section else c.text


def build_index(pdf_paths: list[Path], llm: LLMClient, index_dir: Path = Path(".index")) -> Path:
    """Constrói (ou reaproveita) o índice dos PDFs e devolve o caminho da pasta."""
    pdf_paths = [Path(p) for p in pdf_paths]
    index_path = Path(index_dir) / _index_hash(pdf_paths, llm.embed_model)
    if all((index_path / f).exists() for f in ("chunks.json", "embeddings.npy", "pages.json")):
        return index_path  # cache: nada a fazer

    chunks: list[Chunk] = []
    pages: dict[str, list[str]] = {}
    for path in pdf_paths:
        doc_id = path.stem
        doc_pages = load_pdf(path)
        pages[doc_id] = [text for _, text in doc_pages]
        chunks.extend(chunk_pages(doc_id, doc_pages))

    if not chunks:
        raise ValueError("Nenhum texto extraído dos PDFs (são imagens escaneadas?)")

    # llm.embed já envia em lotes de até 100 textos por chamada.
    embeddings = llm.embed([_embedding_text(c) for c in chunks], batch_size=100)

    # Grava numa pasta temporária e só depois renomeia: se o processo morrer no
    # meio, não fica um índice pela metade que seria "reaproveitado" depois.
    tmp_path = index_path.with_name(index_path.name + ".tmp")
    shutil.rmtree(tmp_path, ignore_errors=True)
    DocumentStore(chunks, embeddings, pages).save(tmp_path)
    shutil.rmtree(index_path, ignore_errors=True)
    tmp_path.rename(index_path)
    return index_path
