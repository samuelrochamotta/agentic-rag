"""Avaliação lado a lado: RAG simples, agêntico e híbrido nas perguntas de eval/questions.json.

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

SYSTEMS = ("simple", "agentic", "hybrid")
LABELS = {"simple": "simples", "agentic": "agêntico", "hybrid": "híbrido"}


def _label(system: str, decider: str | None = None) -> str:
    """'híbrido (jev)': sem o nome do decider, a coluna do híbrido não dá para interpretar."""
    label = LABELS.get(system, system)
    return f"{label} ({decider})" if system == "hybrid" and decider else label


def _systems_in(rows: list[dict]) -> list[str]:
    """Sistemas presentes nos resultados, na ordem de SYSTEMS (o usuário pode rodar só alguns)."""
    return [s for s in SYSTEMS if rows and s in rows[0]]


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

JUDGE_PROMPT = """Você é um avaliador justo. Compare a RESPOSTA de um sistema com a RESPOSTA DE REFERÊNCIA.
A resposta é correta se responde ao que a PERGUNTA pede com os fatos centrais da referência, sem contradizê-los.
- Fatos centrais são os que respondem diretamente à pergunta: o valor, prazo, nome, código ou condição pedidos; \
numa pergunta sobre "do que trata", os assuntos/tópicos; numa pergunta sobre um procedimento, o que acontece.
- Detalhes complementares da referência (exemplos, números que só ilustram um tópico, local exato, observações \
como "não confundir com...") podem faltar sem tornar a resposta incorreta.
- É INCORRETA se contradiz a referência, traz um valor diferente (ex.: de uma versão antiga da política), \
responde a outra coisa ou omite parte central do que foi perguntado (ex.: um dos dois tópicos, um dos itens pedidos).
- Detalhes extras são aceitáveis se não contradizem a referência. Ignore estilo e citações de página.

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

def _evaluate_question(q: dict, store, max_steps: int, systems=SYSTEMS, decider=None) -> dict:
    """Roda os sistemas pedidos numa pergunta.

    Cada sistema ganha seu próprio LLMClient: o Usage é acumulativo e não é
    thread-safe, então compartilhar um cliente entre threads misturaria os custos.
    O store é só leitura e pode ser compartilhado.
    """
    from .agent import run_agent
    from .hybrid import run_hybrid
    from .simple_rag import run_simple

    judge_llm = LLMClient()  # separado: o custo do juiz não conta para os sistemas
    row: dict = {"id": q["id"], "category": q.get("category", "?"), "question": q["question"],
                 "gold": q.get("gold", ""), "must_contain": q.get("must_contain") or []}
    runners = {
        "simple": lambda llm: run_simple(q["question"], store, llm),
        "agentic": lambda llm: run_agent(q["question"], store, llm, max_steps=max_steps),
        "hybrid": lambda llm: run_hybrid(q["question"], store, llm, decider=decider, max_steps=max_steps),
    }
    for name in systems:
        runner = runners[name]
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
    systems: tuple[str, ...] = SYSTEMS,
    decider_kind: str | None = None,
) -> list[dict]:
    from .decider import make_decider

    console = console or Console()
    # O decider é sem estado (o uso vai para o LLMClient de cada pergunta): um só serve a todas as threads.
    decider = make_decider(decider_kind) if "hybrid" in systems else None
    decider_name = decider.name if decider else None
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
        futures = [pool.submit(_evaluate_question, q, store, max_steps, systems, decider) for q in questions]
        for fut in as_completed(futures):
            rows.append(fut.result())
            progress.advance(task)
    # as_completed devolve fora de ordem; reordenamos como no arquivo de perguntas.
    order = {q["id"]: i for i, q in enumerate(questions)}
    rows.sort(key=lambda r: order[r["id"]])

    summary = aggregate(rows)
    notes = []
    if getattr(decider, "cost_missing", False):
        notes.append("Alguma resposta do Jev veio sem usage.cost: o custo do híbrido está subestimado "
                     "(as chamadas e a latência estão contabilizadas).")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(
        json.dumps({"decider": decider_name, "summary": summary, "questions": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (out_dir / "results.md").write_text(render_markdown(rows, summary, decider_name, notes), encoding="utf-8")

    print_tables(rows, summary, console, decider_name)
    for note in notes:
        console.print(f"[yellow]{note}[/]")
    console.print(f"[dim]Tempo total: {time.perf_counter() - t0:.1f}s · resultados em "
                  f"{out_dir / 'results.md'} e {out_dir / 'results.json'}[/]")
    return rows


def regrade(results_path: Path, workers: int = 4, console: Console | None = None) -> list[dict]:
    """Rejulga as respostas já salvas num results.json com o juiz atual.

    Não chama os sistemas de novo: as respostas, o custo e a latência ficam iguais e só o
    veredito muda. Serve para comparar critérios do juiz sem a variação das respostas.
    O veredito anterior fica em `grade.previous` para conferência.
    """
    console = console or Console()
    results_path = Path(results_path)
    data = json.loads(results_path.read_text(encoding="utf-8"))
    rows = data["questions"]
    systems = _systems_in(rows)
    judge_llm = LLMClient()

    def _one(row: dict, system: str) -> None:
        q = {"category": row["category"], "question": row["question"],
             "gold": row.get("gold", ""), "must_contain": row.get("must_contain") or []}
        old = row[system]["grade"]
        try:
            new = grade(q, row[system]["answer"]["text"], judge_llm)
        except Exception as exc:
            new = {"correct": False, "must_contain_ok": None, "missing": [], "judge": None,
                   "reason": f"ERRO no juiz: {exc}"}
        new["previous"] = {"correct": old.get("correct"), "reason": old.get("reason")}
        row[system]["grade"] = new

    jobs = [(r, s) for r in rows for s in systems]
    with Progress(console=console) as progress, ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        task = progress.add_task("Rejulgando", total=len(jobs))
        for fut in as_completed([pool.submit(_one, r, s) for r, s in jobs]):
            fut.result()
            progress.advance(task)

    for r in rows:
        for s in systems:
            g = r[s]["grade"]
            if g["previous"]["correct"] != g["correct"]:
                was, now = _mark(g["previous"]["correct"]), _mark(g["correct"])
                console.print(f"{r['id']} {_label(s, data.get('decider'))}: {was} → {now}  [dim]{g['reason']}[/]")

    summary = aggregate(rows)
    data["summary"] = summary
    results_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    results_path.with_suffix(".md").write_text(render_markdown(rows, summary, data.get("decider")), encoding="utf-8")
    print_tables(rows, summary, console, data.get("decider"))
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
        "avg_decider_calls": sum(u.get("decider_calls", 0) for u in usages) / n,
    }


def aggregate(rows: list[dict]) -> dict:
    """{categoria|"TOTAL": {"simple": stats, "agentic": stats, ...}}"""
    systems = _systems_in(rows)
    categories = sorted({r["category"] for r in rows})
    groups = {c: [r for r in rows if r["category"] == c] for c in categories}
    groups["TOTAL"] = rows
    return {c: {s: _stats(g, s) for s in systems} for c, g in groups.items()}


def _mark(ok: bool) -> str:
    return "✅" if ok else "❌"


def render_markdown(rows: list[dict], summary: dict, decider: str | None = None,
                    notes: list[str] | None = None) -> str:
    systems = _systems_in(rows)
    labels = {s: _label(s, decider) for s in systems}
    lines = ["# Resultados: " + " vs ".join(f"RAG {labels[s]}" for s in systems), ""]
    lines += ["## Por pergunta", "", "| id | categoria | " + " | ".join(labels[s] for s in systems) + " |",
              "|---|---|" + ":-:|" * len(systems)]
    for r in rows:
        marks = " | ".join(_mark(r[s]["grade"]["correct"]) for s in systems)
        lines.append(f"| {r['id']} | {r['category']} | {marks} |")
    lines += ["", "## Agregado por categoria", "",
              "Médias por pergunta, exceto custo total. Latência = tempo gasto nas chamadas à API "
              "(LLM + embeddings), medido pelo `Usage`.", "",
              "Decisões = chamadas ao decider do híbrido; com o Jev elas NÃO aparecem em chamadas LLM.", "",
              "| categoria | sistema | n | acurácia | chamadas LLM (méd.) | decisões (méd.) | tokens (méd.) "
              "| custo US$ (méd.) | custo US$ (total) | latência s (méd.) |",
              "|---|---|--:|--:|--:|--:|--:|--:|--:|--:|"]
    for cat, by_sys in summary.items():
        for s in systems:
            st = by_sys[s]
            name = f"**{cat}**" if cat == "TOTAL" else cat
            lines.append(f"| {name} | {labels[s]} | {st['n']} | {st['accuracy']:.0%} | {st['avg_llm_calls']:.1f} "
                         f"| {st['avg_decider_calls']:.1f} | {st['avg_tokens']:.0f} | {st['avg_cost_usd']:.5f} | {st['total_cost_usd']:.5f} "
                         f"| {st['avg_latency_s']:.1f} |")
    lines += ["", *(f"> {n}" for n in notes or [])]
    if "hybrid" in systems:
        lines += ["", "## Roteamento do híbrido", "", "| id | categoria real | rota | confiança | caminho |",
                  "|---|---|---|--:|---|"]
        for r in rows:
            first = (r["hybrid"]["answer"].get("trace") or [{}])[0]
            args = first.get("args") or {}
            lines.append(f"| {r['id']} | {r['category']} | {args.get('categoria', '—')} "
                         f"| {args.get('confianca', '—')} | {first.get('result_preview', '—')} |")
    lines += ["", "## Erros (motivo do juiz)", ""]
    for r in rows:
        for s in systems:
            g = r[s]["grade"]
            if not g["correct"]:
                lines.append(f"- **{r['id']} / {labels[s]}**: {g['reason']}")
    return "\n".join(lines) + "\n"


def print_tables(rows: list[dict], summary: dict, console: Console, decider: str | None = None) -> None:
    systems = _systems_in(rows)
    per_q = Table(title="Por pergunta")
    for col in ("id", "categoria", *(_label(s, decider) for s in systems)):
        per_q.add_column(col)
    for r in rows:
        per_q.add_row(r["id"], r["category"], *(_mark(r[s]["grade"]["correct"]) for s in systems))
    console.print(per_q)

    agg = Table(title="Agregado (médias por pergunta)")
    for col in ("categoria", "sistema", "acurácia", "chamadas", "decisões", "tokens", "US$ total", "latência s"):
        agg.add_column(col, justify="right" if col not in ("categoria", "sistema") else "left")
    for cat, by_sys in summary.items():
        for s in systems:
            st = by_sys[s]
            agg.add_row(cat, _label(s, decider), f"{st['accuracy']:.0%}", f"{st['avg_llm_calls']:.1f}",
                        f"{st['avg_decider_calls']:.1f}", f"{st['avg_tokens']:.0f}",
                        f"{st['total_cost_usd']:.4f}", f"{st['avg_latency_s']:.1f}",
                        end_section=(s == systems[-1]))
    console.print(agg)
