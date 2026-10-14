"""Linha de comando `rag`.

    rag ingest data/manual_simulado.pdf
    rag ask "pergunta" [--mode agentic|simple|both|hybrid] [--decider jev|llm] [--verbose]
    rag chat [--mode agentic|simple|both|hybrid]
    rag eval [--only q01,q02] [--workers 4] [--systems simple,agentic,hybrid] [--decider jev|llm]
    rag regrade eval/runs/results_jev.json [...]

O caminho do índice ativo fica em `.index/current`, assim `ask/chat/eval` não
precisam receber o índice toda vez.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import settings
from .llm import Answer, LLMClient

console = Console()
CURRENT_FILE = settings.index_dir / "current"


# ---------------------------------------------------------------------------
# Índice ativo
# ---------------------------------------------------------------------------

def _load_store():
    from .store import DocumentStore

    if not CURRENT_FILE.exists():
        console.print("[red]Nenhum índice ativo. Rode primeiro:[/] rag ingest data/manual_simulado.pdf")
        sys.exit(1)
    index_path = Path(CURRENT_FILE.read_text(encoding="utf-8").strip())
    if not index_path.exists():
        console.print(f"[red]Índice registrado não existe mais:[/] {index_path}. Rode `rag ingest` de novo.")
        sys.exit(1)
    return DocumentStore.load(index_path)


# ---------------------------------------------------------------------------
# Exibição
# ---------------------------------------------------------------------------

def _cost_line(answer: Answer) -> str:
    u = answer.usage
    return (f"chamadas LLM: {u.llm_calls} · embeddings: {u.embed_calls} · tokens: {u.total_tokens:,} "
            f"· US$ {u.cost_usd:.5f} · {u.latency_s:.1f}s")


def _show_answer(answer: Answer, title: str, style: str) -> None:
    sources = ", ".join(answer.sources) if answer.sources else "—"
    body = Markdown(answer.text or "(sem resposta)")
    console.print(Panel(body, title=f"[bold]{title}[/]", border_style=style,
                        subtitle=f"[dim]{_cost_line(answer)}[/]"))
    console.print(f"[dim]Fontes: {sources}[/]\n")


def _show_comparison(simple: Answer, agentic: Answer) -> None:
    table = Table(title="Custo comparado")
    table.add_column("métrica")
    table.add_column("simples", justify="right")
    table.add_column("agêntico", justify="right")
    s, a = simple.usage, agentic.usage
    table.add_row("chamadas LLM", str(s.llm_calls), str(a.llm_calls))
    table.add_row("chamadas embedding", str(s.embed_calls), str(a.embed_calls))
    table.add_row("tokens", f"{s.total_tokens:,}", f"{a.total_tokens:,}")
    table.add_row("custo US$", f"{s.cost_usd:.5f}", f"{a.cost_usd:.5f}")
    table.add_row("latência s", f"{s.latency_s:.1f}", f"{a.latency_s:.1f}")
    console.print(table)


def _answer(question: str, mode: str, store, llm: LLMClient, verbose: bool, max_steps: int,
            decider=None) -> None:
    from .agent import run_agent
    from .simple_rag import run_simple

    if mode == "hybrid":
        from .hybrid import describe_route, run_hybrid

        if verbose:
            hybrid = run_hybrid(question, store, llm, decider=decider, max_steps=max_steps, verbose=True,
                                console=console)
        else:
            with console.status("RAG híbrido decidindo..."):
                hybrid = run_hybrid(question, store, llm, decider=decider, max_steps=max_steps)
        console.print(f"[dim]{describe_route(hybrid)}[/]")
        _show_answer(hybrid, f"RAG híbrido ({decider.name})", "magenta")
        return

    simple = agentic = None
    if mode in ("simple", "both"):
        with console.status("RAG simples pensando..."):
            simple = run_simple(question, store, llm)
        _show_answer(simple, "RAG simples", "blue")
    if mode in ("agentic", "both"):
        if verbose:  # com trace, o spinner atrapalharia a saída
            agentic = run_agent(question, store, llm, max_steps=max_steps, verbose=True, console=console)
        else:
            with console.status("RAG agêntico investigando..."):
                agentic = run_agent(question, store, llm, max_steps=max_steps)
        _show_answer(agentic, "RAG agêntico", "green")
    if simple and agentic:
        _show_comparison(simple, agentic)


# ---------------------------------------------------------------------------
# Subcomandos
# ---------------------------------------------------------------------------

def cmd_ingest(args) -> None:
    from .ingest import build_index

    pdfs = [Path(p) for p in args.pdfs]
    for p in pdfs:
        if not p.exists():
            console.print(f"[red]Arquivo não encontrado:[/] {p}")
            sys.exit(1)
    llm = LLMClient()
    with console.status("Lendo PDF, gerando chunks e embeddings..."):
        index_path = build_index(pdfs, llm, settings.index_dir)
    CURRENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CURRENT_FILE.write_text(str(index_path), encoding="utf-8")
    console.print(f"[green]Índice pronto:[/] {index_path}  "
                  f"[dim](embeddings: {llm.usage.embed_calls} chamadas, US$ {llm.usage.cost_usd:.5f})[/]")


def _decider_for(args):
    from .decider import make_decider

    return make_decider(args.decider) if args.mode == "hybrid" else None


def cmd_ask(args) -> None:
    store = _load_store()
    _answer(args.question, args.mode, store, LLMClient(), args.verbose, args.max_steps, _decider_for(args))


def cmd_chat(args) -> None:
    store = _load_store()
    llm = LLMClient()
    decider = _decider_for(args)
    console.print(f"[bold]Chat ({args.mode})[/] — digite sua pergunta; 'sair' ou Ctrl+D para encerrar.")
    while True:
        try:
            question = console.input("[bold cyan]> [/]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if question.lower() in ("sair", "exit", "quit"):
            break
        if question:
            # Cada pergunta é independente (sem memória de conversa): mantém a comparação limpa.
            _answer(question, args.mode, store, llm, args.verbose, args.max_steps, decider)
    console.print(f"[dim]Total da sessão: {llm.usage.llm_calls} chamadas, US$ {llm.usage.cost_usd:.5f}[/]")


def cmd_eval(args) -> None:
    from .evaluate import run_evaluation

    store = _load_store()
    only = [x.strip() for x in args.only.split(",") if x.strip()] if args.only else None
    systems = tuple(x.strip() for x in args.systems.split(",") if x.strip())
    unknown = set(systems) - {"simple", "agentic", "hybrid"}
    if unknown or not systems:
        console.print(f"[red]--systems inválido:[/] {args.systems} (use simple, agentic, hybrid)")
        sys.exit(1)
    run_evaluation(store, questions_path=Path(args.questions), only=only, workers=args.workers,
                   max_steps=args.max_steps, console=console, systems=systems, decider_kind=args.decider)


def cmd_regrade(args) -> None:
    from .evaluate import regrade

    for path in args.results:
        console.rule(path)
        regrade(Path(path), workers=args.workers, console=console)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="rag", description="RAG agêntico vs RAG simples")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest", help="constrói o índice a partir de PDFs")
    p.add_argument("pdfs", nargs="+")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("ask", help="faz uma pergunta")
    p.add_argument("question")
    p.add_argument("--mode", choices=["agentic", "simple", "both", "hybrid"], default="agentic")
    p.add_argument("--decider", choices=["jev", "llm"], default=None,
                   help="quem toma as decisões do modo híbrido (padrão: jev, via OpenRouter)")
    p.add_argument("--verbose", "-v", action="store_true", help="mostra o trace do agente")
    p.add_argument("--max-steps", type=int, default=8)
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("chat", help="REPL interativo")
    p.add_argument("--mode", choices=["agentic", "simple", "both", "hybrid"], default="agentic")
    p.add_argument("--decider", choices=["jev", "llm"], default=None,
                   help="quem toma as decisões do modo híbrido (padrão: jev, via OpenRouter)")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--max-steps", type=int, default=8)
    p.set_defaults(func=cmd_chat)

    p = sub.add_parser("eval", help="roda a avaliação em eval/questions.json")
    p.add_argument("--only", help="ids separados por vírgula, ex.: q01,q02")
    p.add_argument("--workers", type=int, default=4, help="perguntas em paralelo (default 4)")
    p.add_argument("--max-steps", type=int, default=8)
    p.add_argument("--questions", default="eval/questions.json")
    p.add_argument("--systems", default="simple,agentic,hybrid", help="sistemas a avaliar, separados por vírgula")
    p.add_argument("--decider", choices=["jev", "llm"], default=None,
                   help="quem toma as decisões do modo híbrido (padrão: jev, via OpenRouter)")
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("regrade", help="rejulga respostas salvas com o juiz atual (sem rodar os sistemas)")
    p.add_argument("results", nargs="+", help="arquivos results.json")
    p.add_argument("--workers", type=int, default=4)
    p.set_defaults(func=cmd_regrade)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
