"""DocumentStore: o "banco" de chunks e as várias formas de consultá-lo.

Por que tantas formas de busca? Cada uma falha de um jeito diferente:

- **Vetorial (embeddings)**: ótima para paráfrases ("devolução do dinheiro" ~ "reembolso"),
  mas ruim para códigos exatos ("ACX-7741" e "ACX-7714" ficam com vetores quase iguais).
- **BM25 (palavras-chave)**: ótima para termos raros e exatos (códigos, siglas, nomes),
  mas não entende sinônimos.
- **grep (regex)**: não ranqueia nada — devolve TODAS as ocorrências. É o que você quer
  para contar ou enumerar ("quais são todos os códigos de erro?").
- **get_page / neighbors / outline**: não são buscas, são *navegação*. Servem para ler o
  contexto completo depois que uma busca encontrou o ponto certo.

O RAG simples só usa a busca vetorial. O agente pode escolher entre todas.
"""

import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi


@dataclass
class Chunk:
    id: str          # f"{doc_id}:p{page}:c{idx}"  ex.: "manual_simulado:p3:c1"
    doc_id: str      # nome do arquivo sem extensão
    page: int        # 1-based
    idx: int         # índice do chunk dentro da página (0-based)
    text: str
    section: str | None = None   # título de seção detectado (ex.: "4.2 Política de Reembolso")
    # Posição (em caracteres) onde o chunk começa no texto da página. Não está no contrato
    # original do SPEC, mas é útil para o grep: ele procura no texto da PÁGINA (sem
    # duplicatas causadas pela sobreposição) e usa este offset para saber em qual chunk
    # caiu cada ocorrência. Tem default para não quebrar quem cria Chunk sem ele.
    char_start: int = 0


# ---------------------------------------------------------------------------
# Tokenização para o BM25
# ---------------------------------------------------------------------------

# Tokens "compostos" como ACX-7741, v2.3 ou 12/2024: palavras ligadas por - . ou /
_COMPOUND_RE = re.compile(r"\w+(?:[-./]\w+)+")
_WORD_RE = re.compile(r"\w+")


def normalize(text: str) -> str:
    """Minúsculas e sem acentos: 'Política' -> 'politica'.

    NFKD separa a letra do acento ('í' vira 'i' + '´'); depois descartamos os
    caracteres "combinantes" (os acentos). Assim o usuário que digita sem acento
    ainda encontra o termo acentuado.
    """
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def tokenize(text: str) -> list[str]:
    """Quebra o texto em tokens para o BM25.

    'Erro ACX-7741' -> ['erro', 'acx', '7741', 'acx-7741']

    Indexamos as partes ('acx', '7741') E o código inteiro ('acx-7741'). O token
    inteiro é raríssimo no documento, então o BM25 lhe dá um IDF alto — é
    exatamente isso que faz a busca por código exato funcionar bem, mesmo quando
    existem códigos parecidos como ACX-7714.
    """
    norm = normalize(text)
    return _WORD_RE.findall(norm) + _COMPOUND_RE.findall(norm)


# ---------------------------------------------------------------------------
# Detecção de cabeçalhos de seção
# ---------------------------------------------------------------------------

# Linha que começa com numeração tipo "4", "4.2" ou "4.2.1" seguida de texto
# (regex do SPEC: ^\d+(\.\d+)*\s+\S). Ficamos um pouco mais restritivos para não
# confundir linhas de tabela ("3 unidades", "2024 foi...") com títulos:
# números de até 2 dígitos, título começando com letra maiúscula e linha curta.
HEADING_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,2})*\.?)\s+(\S.*)$", re.MULTILINE)


def find_headings(page_text: str) -> list[tuple[int, str]]:
    """Cabeçalhos numerados da página: lista de (posição, título)."""
    found = []
    for m in HEADING_RE.finditer(page_text):
        title = m.group(0).strip()
        if m.group(2)[0].isupper() and len(title) <= 80:
            found.append((m.start(), title))
    return found


# ---------------------------------------------------------------------------
# O store
# ---------------------------------------------------------------------------

class DocumentStore:
    def __init__(self, chunks: list[Chunk], embeddings: np.ndarray, pages: dict[str, list[str]]):
        if len(chunks) != len(embeddings):
            raise ValueError(f"{len(chunks)} chunks mas {len(embeddings)} embeddings")
        self.chunks = chunks
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.pages = pages  # doc_id -> lista de textos de página (índice 0 = página 1)
        self._by_id = {c.id: i for i, c in enumerate(chunks)}

        # O BM25 indexa o título da seção junto com o texto: assim uma busca por
        # "política de reembolso" também acha os chunks do meio da seção 4.2,
        # que muitas vezes não repetem o título no próprio texto.
        corpus = [tokenize(f"{c.section or ''}\n{c.text}") for c in chunks]
        # BM25Okapi quebra com corpus vazio; um índice vazio simplesmente não acha nada.
        self._bm25 = BM25Okapi(corpus) if corpus else None

    # -- construção ----------------------------------------------------------

    @classmethod
    def from_chunks(cls, chunks: list[Chunk], embeddings: np.ndarray | None = None,
                    pages: dict[str, list[str]] | None = None) -> "DocumentStore":
        """Monta um store em memória (útil em testes, sem precisar de disco nem API).

        - Sem `embeddings`: usa zeros (a busca vetorial fica inútil, o resto funciona).
        - Sem `pages`: reconstrói cada página concatenando seus chunks (aproximação,
          pois a sobreposição entre chunks aparece duplicada).
        """
        if embeddings is None:
            embeddings = np.zeros((len(chunks), 1), dtype=np.float32)
        if pages is None:
            pages = {}
            for c in chunks:
                doc_pages = pages.setdefault(c.doc_id, [])
                while len(doc_pages) < c.page:
                    doc_pages.append("")
                doc_pages[c.page - 1] = (doc_pages[c.page - 1] + "\n" + c.text).strip()
        return cls(chunks, embeddings, pages)

    @classmethod
    def load(cls, index_path: Path) -> "DocumentStore":
        """Carrega um índice gravado por `ingest.build_index`."""
        index_path = Path(index_path)
        raw_chunks = json.loads((index_path / "chunks.json").read_text(encoding="utf-8"))
        chunks = [Chunk(**c) for c in raw_chunks]
        embeddings = np.load(index_path / "embeddings.npy")
        pages = json.loads((index_path / "pages.json").read_text(encoding="utf-8"))
        return cls.from_chunks(chunks, embeddings, pages)

    def save(self, index_path: Path) -> None:
        """Grava o índice no formato que `load` lê (usado pelo ingest)."""
        index_path = Path(index_path)
        index_path.mkdir(parents=True, exist_ok=True)
        (index_path / "chunks.json").write_text(
            json.dumps([asdict(c) for c in self.chunks], ensure_ascii=False, indent=1), encoding="utf-8")
        np.save(index_path / "embeddings.npy", self.embeddings.astype(np.float32))
        (index_path / "pages.json").write_text(
            json.dumps(self.pages, ensure_ascii=False, indent=1), encoding="utf-8")

    # -- buscas ---------------------------------------------------------------

    def bm25_search(self, query: str, k: int = 5) -> list[tuple[Chunk, float]]:
        """Busca por palavras-chave (BM25). Só devolve chunks com score > 0."""
        if self._bm25 is None:
            return []
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        scores = self._bm25.get_scores(q_tokens)
        order = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in order if scores[i] > 0]

    def vector_search(self, query_vec: np.ndarray, k: int = 5) -> list[tuple[Chunk, float]]:
        """Busca por similaridade de cosseno.

        Os embeddings já estão normalizados (norma 1), então cosseno = produto escalar.
        Normalizamos a query também, por segurança.
        """
        if not self.chunks:
            return []
        q = np.asarray(query_vec, dtype=np.float32).reshape(-1)
        q = q / max(float(np.linalg.norm(q)), 1e-12)
        scores = self.embeddings @ q
        order = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in order]

    def grep(self, pattern: str, max_hits: int = 20) -> list[tuple[Chunk, str]]:
        """Todas as ocorrências de uma regex (case-insensitive), com um trecho ao redor.

        Procuramos no texto das PÁGINAS, não dos chunks: como chunks vizinhos se
        sobrepõem, procurar neles contaria a mesma ocorrência duas vezes — o que
        estragaria justamente o uso principal do grep, que é contar/enumerar.
        Se o padrão não for uma regex válida, ele é tratado como texto literal.
        """
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        hits: list[tuple[Chunk, str]] = []
        for doc_id, doc_pages in self.pages.items():
            for page_num, page_text in enumerate(doc_pages, start=1):
                for m in regex.finditer(page_text):
                    if m.end() == m.start():
                        continue  # ignora matches vazios (ex.: padrão "a*")
                    chunk = self._chunk_at(doc_id, page_num, m.start())
                    if chunk is None:
                        continue
                    lo, hi = max(0, m.start() - 80), min(len(page_text), m.end() + 80)
                    snippet = page_text[lo:hi].replace("\n", " ")
                    snippet = ("…" if lo > 0 else "") + snippet + ("…" if hi < len(page_text) else "")
                    hits.append((chunk, snippet))
                    if len(hits) >= max_hits:
                        return hits
        return hits

    def _chunk_at(self, doc_id: str, page: int, pos: int) -> Chunk | None:
        """O chunk da página que contém a posição `pos` (o último que começa antes dela)."""
        best = None
        for c in self.chunks:
            if c.doc_id == doc_id and c.page == page and c.char_start <= pos:
                if best is None or c.char_start > best.char_start:
                    best = c
        return best

    # -- navegação ------------------------------------------------------------

    def get_chunk(self, chunk_id: str) -> Chunk | None:
        i = self._by_id.get(chunk_id)
        return None if i is None else self.chunks[i]

    def neighbors(self, chunk_id: str, window: int = 1) -> list[Chunk]:
        """O chunk e seus `window` vizinhos de cada lado, no mesmo documento.

        Pode atravessar páginas: o fim da página 3 continua no começo da página 4.
        Pressupõe que `self.chunks` está na ordem de leitura (é como o ingest grava).
        """
        i = self._by_id.get(chunk_id)
        if i is None:
            return []
        doc_id = self.chunks[i].doc_id
        lo, hi = max(0, i - window), min(len(self.chunks), i + window + 1)
        return [c for c in self.chunks[lo:hi] if c.doc_id == doc_id]

    def get_page(self, doc_id: str, page: int) -> str | None:
        doc_pages = self.pages.get(doc_id)
        if doc_pages is None or not 1 <= page <= len(doc_pages):
            return None
        return doc_pages[page - 1]

    def outline(self) -> list[dict]:
        """Sumário: cada seção, uma vez, na ordem em que aparece.

        Lemos os cabeçalhos direto do texto das páginas (e não do campo `section`
        dos chunks): se duas seções curtas caem no mesmo chunk, o chunk só guarda
        a última — mas o sumário precisa mostrar as duas.
        """
        seen: set[tuple[str, str]] = set()
        result = []
        for doc_id, doc_pages in self.pages.items():
            for page_num, page_text in enumerate(doc_pages, start=1):
                for _, title in find_headings(page_text):
                    if (doc_id, title) not in seen:
                        seen.add((doc_id, title))
                        result.append({"doc_id": doc_id, "page": page_num, "section": title})
        return result

    def doc_ids(self) -> list[str]:
        return list(dict.fromkeys(c.doc_id for c in self.chunks))
