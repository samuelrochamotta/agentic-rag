"""FinanceBench: um juiz externo que o autor deste projeto não escreveu.

O conjunto aberto (patronus-ai/financebench) tem 150 perguntas sobre 84 relatórios
financeiros (10-K, 10-Q, 8-K) em PDF, com resposta e página de evidência anotadas por
humanos. Como no artigo original (Islam et al., 2023, configuração "single store"),
cada pergunta é feita sobre um índice só do documento dela.

Medimos três coisas por pergunta:
- correct: o juiz (JUDGE_MODEL) considera a resposta equivalente ao gabarito;
- evidence_hit: a página de evidência do gabarito está entre as fontes do sistema
  (separa erro de recuperação de erro de leitura/cálculo);
- citações: a mesma checagem determinística do `rag eval`.

Prepare os dados com:
    mkdir -p data/financebench/pdfs
    curl -L -o data/financebench/financebench_open_source.jsonl \\
      https://raw.githubusercontent.com/patronus-ai/financebench/main/data/financebench_open_source.jsonl
    # e um PDF por doc_name em data/financebench/pdfs/<doc_name>.pdf (mesmo repositório, pasta pdfs/)
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from .config import settings
from .evaluate import _parse_judge_json, _pct, _store_pages, check_citations
from .ingest import build_index
from .llm import Answer, LLMClient, Usage
from .store import DocumentStore

DATA_DIR = Path("data/financebench")
INDEX_DIR = Path(".index/financebench")

# Mesmo espírito do avaliador do artigo: o número certo importa, a formatação não.
JUDGE_PROMPT = """You are grading answers to financial questions about SEC filings.
Compare the SYSTEM ANSWER with the GOLD ANSWER (the system may answer in Portuguese).
The answer is correct if it states the same key value or conclusion as the gold answer:
- numbers may differ in formatting, units written out (USD millions vs $ billions) or small rounding \
(up to ~1% relative, or the last displayed digit);
- for yes/no or judgment questions, the conclusion must match and must not contradict the gold reasoning;
- extra details are fine unless they contradict the gold answer;
- a refusal ("not found", "não encontrei") is incorrect unless the gold answer says it cannot be determined.

Reply ONLY with JSON: {"correct": true|false, "reason": "short justification"}"""


def load_questions(path: Path = DATA_DIR / "financebench_open_source.jsonl") -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def evidence_pages(q: dict) -> set[int]:
    """Páginas de evidência no formato do store (1-based); o FinanceBench usa 0-based."""
    return {int(e["evidence_page_num"]) + 1 for e in q.get("evidence") or [] if "evidence_page_num" in e}


_SOURCE_PAGE_RE = re.compile(r":p(\d+):")


def source_pages(answer: Answer) -> set[int]:
    """Páginas vistas pelo sistema: chunks retornados pelas ferramentas + read_page do trace."""
    pages = {int(m.group(1)) for s in answer.sources for m in [_SOURCE_PAGE_RE.search(s)] if m}
    for step in answer.trace or []:
        if step.get("tool") == "read_page" and str((step.get("args") or {}).get("page", "")).isdigit():
            pages.add(int(step["args"]["page"]))
    return pages


def truncated_pages(answer: Answer) -> set[int]:
    """Páginas lidas com read_page cujo texto foi cortado (MAX_OUTPUT_CHARS): a evidência pode ter ficado de fora."""
    return {int(step["args"]["page"]) for step in answer.trace or []
            if step.get("tool") == "read_page" and step.get("truncated")
            and str((step.get("args") or {}).get("page", "")).isdigit()}


def judge(q: dict, answer_text: str, judge_llm) -> dict:
    messages = [
        {"role": "system", "content": JUDGE_PROMPT},
        {"role": "user", "content": f"QUESTION:\n{q['question']}\n\nGOLD ANSWER:\n{q['answer']}\n\n"
                                    f"SYSTEM ANSWER:\n{answer_text}"},
    ]
    try:
        msg = judge_llm.chat(messages, response_format={"type": "json_object"})
    except Exception:
        msg = judge_llm.chat(messages)
    return _parse_judge_json(msg.content or "")


def build_indexes(questions: list[dict], workers: int = 4, console: Console | None = None) -> dict[str, Path]:
    """Um índice por documento (cacheado em .index/financebench/<hash>)."""
    console = console or Console()
    docs = sorted({q["doc_name"] for q in questions})
    missing = [d for d in docs if not (DATA_DIR / "pdfs" / f"{d}.pdf").exists()]
    if missing:
        raise FileNotFoundError(f"PDFs ausentes em {DATA_DIR / 'pdfs'}: {missing[:5]}...")
    out: dict[str, Path] = {}
    usage = Usage()

    def _one(doc: str) -> tuple[str, Path, Usage]:
        llm = LLMClient()
        return doc, build_index([DATA_DIR / "pdfs" / f"{doc}.pdf"], llm, INDEX_DIR), llm.usage

    with Progress(console=console) as progress, ThreadPoolExecutor(max_workers=workers) as pool:
        task = progress.add_task("Indexando", total=len(docs))
        for fut in as_completed([pool.submit(_one, d) for d in docs]):
            doc, path, u = fut.result()
            out[doc] = path
            usage.add(u)
            progress.advance(task)
    console.print(f"[dim]Índices: {len(out)} documentos · embeddings US$ {usage.cost_usd:.4f}[/]")
    return out


def _run_one(q: dict, index_path: Path, system: str, max_steps: int) -> dict:
    from .agent import run_agent
    from .simple_rag import run_simple

    store = DocumentStore.load(index_path)
    llm = LLMClient()
    try:
        if system == "simple":
            answer = run_simple(q["question"], store, llm)
        else:
            answer = run_agent(q["question"], store, llm, max_steps=max_steps)
    except Exception as exc:
        answer = Answer(text=f"ERRO ao executar: {exc}", sources=[], usage=llm.usage)
    try:
        verdict = judge(q, answer.text, LLMClient(chat_model=settings.judge_model))
    except Exception as exc:
        verdict = {"correct": None, "reason": f"ERRO no juiz: {exc}"}
    gold_pages = evidence_pages(q)
    return {
        "id": q["financebench_id"], "doc": q["doc_name"], "type": q.get("question_type"),
        "reasoning": q.get("question_reasoning"), "question": q["question"], "gold": q["answer"],
        "system": system, "answer": asdict(answer), "correct": verdict["correct"], "reason": verdict["reason"],
        "evidence_pages": sorted(gold_pages),
        "evidence_hit": bool(gold_pages & source_pages(answer)) if gold_pages else None,
        "evidence_truncated": bool(gold_pages & truncated_pages(answer)),
        "citations": check_citations(answer.text, _store_pages(store)),
    }


def run(systems: tuple[str, ...] = ("agentic",), limit: int | None = None, only: list[str] | None = None,
        workers: int = 6, max_steps: int = 8, out_dir: Path = Path("eval/financebench"),
        console: Console | None = None) -> list[dict]:
    console = console or Console()
    questions = load_questions()
    if only:
        questions = [q for q in questions if q["financebench_id"] in set(only)]
    if limit:
        questions = questions[:limit]
    indexes = build_indexes(questions, console=console)

    rows: list[dict] = []
    t0 = time.perf_counter()
    jobs = [(q, s) for q in questions for s in systems]
    with Progress(console=console) as progress, ThreadPoolExecutor(max_workers=workers) as pool:
        task = progress.add_task("FinanceBench", total=len(jobs))
        futures = [pool.submit(_run_one, q, indexes[q["doc_name"]], s, max_steps) for q, s in jobs]
        for fut in as_completed(futures):
            rows.append(fut.result())
            progress.advance(task)
    order = {q["financebench_id"]: i for i, q in enumerate(questions)}
    rows.sort(key=lambda r: (order[r["id"]], r["system"]))

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"chat_model": settings.chat_model, "judge_model": settings.judge_model,
            "embed_model": settings.embed_model, "max_steps": max_steps}
    (out_dir / "results.json").write_text(json.dumps({**meta, "rows": rows}, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    md = render_markdown(rows, meta)
    (out_dir / "results.md").write_text(md, encoding="utf-8")
    console.print(md)
    console.print(f"[dim]Tempo total: {time.perf_counter() - t0:.1f}s · {out_dir / 'results.md'}[/]")
    return rows


def _summary(rows: list[dict]) -> dict:
    # correct=None é falha do juiz, não da resposta: fica fora da acurácia e aparece em judge_errors.
    judge_errors = sum(r["correct"] is None for r in rows)
    graded = [r for r in rows if r["correct"] is not None]
    n = len(rows)
    usages = [r["answer"]["usage"] for r in rows]
    hits = [r["evidence_hit"] for r in rows if r["evidence_hit"] is not None]
    sup = sum(r["citations"]["supported"] for r in rows)
    els = sum(r["citations"]["elsewhere"] for r in rows)
    return {
        "n": n, "judge_errors": judge_errors,
        "accuracy": sum(r["correct"] for r in graded) / len(graded) if graded else 0.0,
        "evidence_recall": sum(hits) / len(hits) if hits else None,
        # Erros com a evidência em mãos = falha de leitura/cálculo, não de busca.
        "wrong_with_evidence": sum(1 for r in rows if r["correct"] is False and r["evidence_hit"]
                                   and not r.get("evidence_truncated")),
        "evidence_truncated": sum(1 for r in rows if r.get("evidence_truncated")),
        "citation_precision": sup / (sup + els) if sup + els else None,
        "avg_cost_usd": sum(u["cost_usd"] for u in usages) / n,
        "total_cost_usd": sum(u["cost_usd"] for u in usages),
        "avg_latency_s": sum(u["latency_s"] for u in usages) / n,
        "avg_llm_calls": sum(u["llm_calls"] for u in usages) / n,
    }


def render_markdown(rows: list[dict], meta: dict) -> str:
    systems = sorted({r["system"] for r in rows})
    lines = [f"# FinanceBench (open source) · chat `{meta['chat_model']}` · juiz `{meta['judge_model']}`", "",
             "Um índice por documento (configuração *single store* do artigo). `recall de evidência` = a página "
             "anotada pelos autores está entre as que o sistema viu. \"Erros com evidência em mãos\" exclui as "
             "perguntas em que o read_page da página de evidência foi truncado (contadas à parte).", "",
             "| sistema | grupo | n | erros do juiz | acurácia | recall de evidência | erros com evidência em mãos "
             "| página de evidência truncada "
             "| precisão de citação | US$/pergunta | US$ total | latência s | chamadas LLM |",
             "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for s in systems:
        mine = [r for r in rows if r["system"] == s]
        groups = {"TOTAL": mine} | {t: [r for r in mine if r["type"] == t] for t in sorted({r["type"] for r in mine})}
        for g, rs in groups.items():
            st = _summary(rs)
            lines.append(f"| {s} | {'**TOTAL**' if g == 'TOTAL' else g} | {st['n']} | {st['judge_errors']} | {st['accuracy']:.1%} "
                         f"| {_pct(st['evidence_recall'])} | {st['wrong_with_evidence']} | {st['evidence_truncated']} "
                         f"| {_pct(st['citation_precision'])} | {st['avg_cost_usd']:.5f} | {st['total_cost_usd']:.4f} "
                         f"| {st['avg_latency_s']:.1f} | {st['avg_llm_calls']:.1f} |")
    lines += ["", "## Erros", ""]
    for r in rows:
        if r["correct"] is not True:
            hit = {True: "evidência vista", False: "evidência NÃO vista", None: "sem página anotada"}[r["evidence_hit"]]
            lines.append(f"- **{r['id']}** ({r['system']}, {r['doc']}, {hit}): {r['reason']}")
    return "\n".join(lines) + "\n"
