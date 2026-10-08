"""RAG simples (baseline): embeda a pergunta → top-k por similaridade → uma chamada ao LLM.

Propositalmente ingênuo: sem busca híbrida, sem rerank, sem reescrever a pergunta.
É o "RAG de tutorial", que serve de régua para medir o ganho (e o custo) do agêntico.
"""

from __future__ import annotations

from .llm import Answer
from .prompts import ANSWER_RULES

SYSTEM_PROMPT = f"""Você responde perguntas sobre um documento usando somente os trechos fornecidos.
Cada trecho vem com sua página no cabeçalho.

{ANSWER_RULES}"""


def _format_context(hits) -> str:
    blocks = []
    for chunk, score in hits:
        header = f"[chunk {chunk.id} | p. {chunk.page}"
        if chunk.section:
            header += f" | seção: {chunk.section}"
        blocks.append(f"{header}]\n{chunk.text}")
    return "\n\n---\n\n".join(blocks)


def run_simple(question: str, store, llm, k: int = 5) -> Answer:
    usage_before = llm.usage.snapshot()

    # 1) Recuperação: um único embedding e um único top-k. Se os trechos certos
    #    não estiverem entre os k mais parecidos, o modelo simplesmente não os verá.
    query_vec = llm.embed([question])[0]
    hits = store.vector_search(query_vec, k=k)

    # 2) Geração: uma única chamada de chat com os trechos colados no prompt.
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Trechos do documento:\n\n{_format_context(hits)}\n\nPergunta: {question}"},
    ]
    msg = llm.chat(messages)

    return Answer(
        text=msg.content or "",
        sources=[chunk.id for chunk, _ in hits],
        usage=llm.usage.since(usage_before),
    )
