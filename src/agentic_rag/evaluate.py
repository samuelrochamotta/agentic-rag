"""Avaliação lado a lado: RAG simples vs RAG agêntico nas perguntas de eval/questions.json.

Critério de acerto (ver SPEC):
- `must_contain` (se houver): todos os termos precisam aparecer na resposta
  (comparação sem diferenciar maiúsculas/minúsculas nem acentos);
- E um juiz LLM (LLM-as-judge) compara a resposta com a resposta de referência (`gold`);
- Categoria `sem_resposta`: correto = a resposta admite que a informação não está no documento.

O custo do juiz NÃO entra na conta dos sistemas: ele usa um LLMClient próprio.
"""

from __future__ import annotations

import json
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from .llm import Answer, LLMClient, Usage

SYSTEMS = ("simple", "agentic")


# ---------------------------------------------------------------------------
# Checagens determinísticas (funções puras — fáceis de testar offline)
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Minúsculas + sem acentos + espaços colapsados: 'Reembolso  SÓ' -> 'reembolso so'."""
    decomposed = unicodedata.normalize("NFKD", text or "")
    no_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return " ".join(no_accents.casefold().split())


def missing_terms(text: str, terms: list[str]) -> list[str]:
    """Termos de `must_contain` que NÃO aparecem na resposta."""
    norm_text = normalize(text)
    return [t for t in terms if normalize(t) not in norm_text]


def must_contain_ok(text: str, terms: list[str] | None) -> bool:
    return not missing_terms(text, terms or [])


# Variações comuns de "não encontrei" (já normalizadas: sem acento, minúsculas).
_NOT_FOUND_PATTERNS = [
    r"nao encontrei",
    r"nao (foi|foram) encontrad",
    r"nao (esta|estao|consta|constam|aparece|aparecem)\b.{0,40}\bdocumento",
    r"nao ha (nenhuma )?(informac|mencao|evidenc|dados)",
    r"documento nao (menciona|informa|traz|contem|especifica|apresenta|cita)",
    r"nao (e|sao) (mencionad|informad|especificad)",
]


def declares_not_found(text: str) -> bool:
    norm = normalize(text)
    return any(re.search(p, norm) for p in _NOT_FOUND_PATTERNS)


# ---------------------------------------------------------------------------
# Juiz LLM
# ---------------------------------------------------------------------------

JUDGE_PROMPT = """Você é um avaliador rigoroso. Compare a RESPOSTA de um sistema com a RESPOSTA DE REFERÊNCIA.
A resposta é correta se contém os fatos essenciais da referência (números, prazos, nomes, condições) \
sem contradizê-los. Detalhes extras são aceitáveis se não contradizem a referência; omitir um fato \
essencial ou trazer um valor diferente (ex.: de uma versão antiga da política) torna a resposta incorreta.
Ignore estilo e citações de página.

Responda SOMENTE com JSON: {"correct": true|false, "reason": "justificativa curta"}"""


def _parse_judge_json(raw: str) -> dict:
    """Parse tolerante: JSON puro → primeiro {...} no texto → procura 'true/false'."""
    raw = raw or ""
    for candidate in (raw, *re.findall(r"\{.*\}", raw, flags=re.DOTALL)):
        try:
            data = json.loads(candidate)
            if isinstance(data, dict) and "correct" in data:
                correct = data["correct"]
                if isinstance(correct, str):
                    correct = correct.strip().lower() in ("true", "sim", "yes", "1")
                return {"correct": bool(correct), "reason": str(data.get("reason", ""))}
        except json.JSONDecodeError:
            continue
    m = re.search(r'"?correct"?\s*:\s*(true|false)', raw, flags=re.IGNORECASE)
    if m:
        return {"correct": m.group(1).lower() == "true", "reason": "(parse parcial) " + raw[:200]}
    return {"correct": False, "reason": "não foi possível interpretar o juiz: " + raw[:200]}


def judge(question: str, gold: str, answer_text: str, judge_llm) -> dict:
    messages = [
        {"role": "system", "content": JUDGE_PROMPT},
        {"role": "user", "content": f"PERGUNTA:\n{question}\n\nRESPOSTA DE REFERÊNCIA:\n{gold}\n\nRESPOSTA:\n{answer_text}"},
    ]
    try:
        msg = judge_llm.chat(messages, response_format={"type": "json_object"})
    except Exception:
        # Alguns provedores do OpenRouter não aceitam response_format; tentamos sem.
        msg = judge_llm.chat(messages)
    return _parse_judge_json(msg.content or "")


def grade(q: dict, answer_text: str, judge_llm) -> dict:
    """Aplica o critério do SPEC e devolve um dicionário com o veredito e o porquê."""
    if q.get("category") == "sem_resposta":
        ok = declares_not_found(answer_text)
        return {"correct": ok, "must_contain_ok": None, "missing": [], "judge": None,
                "reason": "declarou ausência" if ok else "não declarou que a informação não está no documento"}

    terms = q.get("must_contain") or []
    missing = missing_terms(answer_text, terms)
    verdict = judge(q["question"], q.get("gold", ""), answer_text, judge_llm)
    correct = verdict["correct"] and not missing
    reason = verdict["reason"]
    if missing:
        reason = f"faltam termos {missing}; juiz: {reason}"
    return {"correct": correct, "must_contain_ok": not missing, "missing": missing,
            "judge": verdict["correct"], "reason": reason}


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def _evaluate_question(q: dict, store, max_steps: int) -> dict:
    """Roda os dois sistemas numa pergunta.

    Cada sistema ganha seu próprio LLMClient: o Usage é acumulativo e não é
    thread-safe, então compartilhar um cliente entre threads misturaria os custos.
    O store é só leitura e pode ser compartilhado.
    """
    from .agent import run_agent
    from .simple_rag import run_simple

    judge_llm = LLMClient()  # separado: o custo do juiz não conta para os sistemas
    row: dict = {"id": q["id"], "category": q.get("category", "?"), "question": q["question"],
                 "gold": q.get("gold", ""), "must_contain": q.get("must_contain") or []}
    runners = {
        "simple": lambda llm: run_simple(q["question"], store, llm),
        "agentic": lambda llm: run_agent(q["question"], store, llm, max_steps=max_steps),
    }
    for name, runner in runners.items():
        try:
            answer: Answer = runner(LLMClient())
        except Exception as exc:  # uma falha não deve derrubar a avaliação inteira
            answer = Answer(text=f"ERRO ao executar: {exc}", sources=[], usage=Usage())
        try:
            verdict = grade(q, answer.text, judge_llm)
        except Exception as exc:
            verdict = {"correct": False, "must_contain_ok": None, "missing": [], "judge": None,
                       "reason": f"ERRO no juiz: {exc}"}
        row[name] = {"answer": asdict(answer), "grade": verdict}
    return row


def run_evaluation(
    store,
    questions_path: Path = Path("eval/questions.json"),
    out_dir: Path = Path("eval"),
    only: list[str] | None = None,
    workers: int = 4,
    max_steps: int = 8,
    console: Console | None = None,
) -> list[dict]:
    console = console or Console()
    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))
    if only:
        wanted = set(only)
        questions = [q for q in questions if q["id"] in wanted]
    if not questions:
        console.print("[red]Nenhuma pergunta selecionada.[/]")
        return []

    rows: list[dict] = []
    t0 = time.perf_counter()
    with Progress(console=console) as progress, ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        task = progress.add_task("Avaliando", total=len(questions))
        futures = [pool.submit(_evaluate_question, q, store, max_steps) for q in questions]
        for fut in as_completed(futures):
            rows.append(fut.result())
            progress.advance(task)
    # as_completed devolve fora de ordem; reordenamos como no arquivo de perguntas.
    order = {q["id"]: i for i, q in enumerate(questions)}
    rows.sort(key=lambda r: order[r["id"]])

    summary = aggregate(rows)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(
        json.dumps({"summary": summary, "questions": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "results.md").write_text(render_markdown(rows, summary), encoding="utf-8")

    print_tables(rows, summary, console)
    console.print(f"[dim]Tempo total: {time.perf_counter() - t0:.1f}s · resultados em "
                  f"{out_dir / 'results.md'} e {out_dir / 'results.json'}[/]")
    return rows


# ---------------------------------------------------------------------------
# Agregação e relatórios
# ---------------------------------------------------------------------------

def _stats(rows: list[dict], system: str) -> dict:
    n = len(rows)
    if n == 0:
        return {}
    usages = [r[system]["answer"]["usage"] for r in rows]
    tokens = [u["prompt_tokens"] + u["completion_tokens"] for u in usages]
    return {
        "n": n,
        "accuracy": sum(r[system]["grade"]["correct"] for r in rows) / n,
        "avg_llm_calls": sum(u["llm_calls"] for u in usages) / n,
        "avg_tokens": sum(tokens) / n,
        "total_cost_usd": sum(u["cost_usd"] for u in usages),
        "avg_cost_usd": sum(u["cost_usd"] for u in usages) / n,
        "avg_latency_s": sum(u["latency_s"] for u in usages) / n,
    }


def aggregate(rows: list[dict]) -> dict:
    """{categoria|"TOTAL": {"simple": stats, "agentic": stats}}"""
    categories = sorted({r["category"] for r in rows})
    groups = {c: [r for r in rows if r["category"] == c] for c in categories}
    groups["TOTAL"] = rows
    return {c: {s: _stats(g, s) for s in SYSTEMS} for c, g in groups.items()}


def _mark(ok: bool) -> str:
    return "✅" if ok else "❌"


def render_markdown(rows: list[dict], summary: dict) -> str:
    lines = ["# Resultados: RAG simples vs RAG agêntico", ""]
    lines += ["## Por pergunta", "", "| id | categoria | simples | agêntico |", "|---|---|:-:|:-:|"]
    for r in rows:
        lines.append(f"| {r['id']} | {r['category']} | {_mark(r['simple']['grade']['correct'])} "
                     f"| {_mark(r['agentic']['grade']['correct'])} |")
    lines += ["", "## Agregado por categoria", "",
              "Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API "
              "(LLM + embeddings), medido pelo `Usage`.", "",
              "| categoria | sistema | n | acurácia | chamadas LLM (méd.) | tokens (méd.) "
              "| custo US$ (méd.) | custo US$ (total) | latência s (méd.) |",
              "|---|---|--:|--:|--:|--:|--:|--:|--:|"]
    labels = {"simple": "simples", "agentic": "agêntico"}
    for cat, by_sys in summary.items():
        for s in SYSTEMS:
            st = by_sys[s]
            name = f"**{cat}**" if cat == "TOTAL" else cat
            lines.append(f"| {name} | {labels[s]} | {st['n']} | {st['accuracy']:.0%} | {st['avg_llm_calls']:.1f} "
                         f"| {st['avg_tokens']:.0f} | {st['avg_cost_usd']:.5f} | {st['total_cost_usd']:.5f} "
                         f"| {st['avg_latency_s']:.1f} |")
    lines += ["", "## Erros (motivo do juiz)", ""]
    for r in rows:
        for s in SYSTEMS:
            g = r[s]["grade"]
            if not g["correct"]:
                lines.append(f"- **{r['id']} / {labels[s]}**: {g['reason']}")
    return "\n".join(lines) + "\n"


def print_tables(rows: list[dict], summary: dict, console: Console) -> None:
    per_q = Table(title="Por pergunta")
    for col in ("id", "categoria", "simples", "agêntico"):
        per_q.add_column(col)
    for r in rows:
        per_q.add_row(r["id"], r["category"], _mark(r["simple"]["grade"]["correct"]),
                      _mark(r["agentic"]["grade"]["correct"]))
    console.print(per_q)

    agg = Table(title="Agregado (médias por pergunta)")
    for col in ("categoria", "sistema", "acurácia", "chamadas", "tokens", "US$ total", "latência s"):
        agg.add_column(col, justify="right" if col not in ("categoria", "sistema") else "left")
    for cat, by_sys in summary.items():
        for s in SYSTEMS:
            st = by_sys[s]
            agg.add_row(cat, s, f"{st['accuracy']:.0%}", f"{st['avg_llm_calls']:.1f}", f"{st['avg_tokens']:.0f}",
                        f"{st['total_cost_usd']:.4f}", f"{st['avg_latency_s']:.1f}",
                        end_section=(s == SYSTEMS[-1]))
    console.print(agg)
