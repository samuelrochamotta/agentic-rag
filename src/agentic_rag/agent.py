"""RAG agêntico: o LLM decide COMO buscar, em várias rodadas, usando ferramentas.

O coração deste módulo é um loop explícito de *tool calling* (sem frameworks), para
que fique visível o ciclo clássico de um agente:

    PENSAR  -> o modelo lê a conversa e decide: responder ou chamar ferramentas?
    AGIR    -> nós (código Python) executamos as ferramentas que ele pediu
    OBSERVAR-> devolvemos os resultados como mensagens role="tool" e repetimos

O modelo nunca executa nada sozinho: ele só *pede* chamadas (tool_calls) e quem
executa é o nosso código. Isso é importante para segurança e para depuração.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from rich.console import Console
from rich.panel import Panel

from .llm import Answer
from .prompts import ANSWER_RULES, NOT_FOUND

SYSTEM_PROMPT = f"""Você é um assistente de pesquisa que responde perguntas sobre documentos \
(manuais, políticas, relatórios) usando ferramentas de busca. Você NÃO conhece o documento de \
antemão: toda resposta precisa vir de evidências encontradas com as ferramentas.

Como trabalhar:
1. Planeje antes de agir: o que a pergunta pede? Quais termos, códigos, seções ou números \
precisam ser encontrados? A pergunta tem várias partes que exigem buscas separadas?
2. Escolha a ferramenta adequada:
   - list_outline: comece por ela quando a pergunta citar uma seção, capítulo ou página, ou \
quando precisar se orientar na estrutura do documento.
   - search_keyword: termos exatos — códigos (ex.: ACX-7741), siglas, nomes próprios, números.
   - search_semantic: quando a pergunta usa palavras diferentes das do documento (paráfrases).
   - grep: para CONTAR ou ENUMERAR todas as ocorrências de algo (a busca top-k pode omitir itens).
   - read_page: para ler tabelas e o contexto completo de uma página.
   - read_neighbors: quando um trecho parece cortado e você precisa do texto ao redor.
   - calculator: para qualquer conta (somas, multiplicações, percentuais). Não faça contas de cabeça.
3. Desconfie de distratores: documentos costumam ter versões antigas e vigentes de uma mesma \
política, exceções, notas de rodapé e revogações. Verifique datas, números de versão e termos \
como "vigente", "substitui", "revogado" antes de responder.
4. Combine evidências de várias partes do documento quando a pergunta exigir (multi-hop): \
encontre cada peça e só então junte.
5. Pode chamar várias ferramentas no mesmo passo quando as buscas forem independentes.
6. Pare de buscar quando tiver evidência suficiente. Se, após buscar de formas diferentes, \
não houver evidência, diga "{NOT_FOUND}."

{ANSWER_RULES}"""

FORCE_FINAL_PROMPT = (
    "Você atingiu o limite de passos de busca. Não chame mais ferramentas. "
    "Com base APENAS no que já foi encontrado acima, escreva agora a melhor resposta final possível, "
    f"citando páginas [p. N]. Se as evidências forem insuficientes, diga \"{NOT_FOUND}.\""
)

# Formato de chunk_id definido no SPEC: "<doc_id>:p<página>:c<índice>".
CHUNK_ID_RE = re.compile(r"[\w.\-]+:p\d+:c\d+")


def _collect_chunk_ids(result: str) -> list[str]:
    """Extrai os chunk_ids que apareceram no resultado de uma ferramenta.

    Primeiro tentamos interpretar o resultado como JSON e procurar chaves "chunk_id"
    (forma mais confiável). Se não for JSON (ex.: texto puro ou "ERRO: ..."), caímos
    para uma regex no formato fixo do SPEC.
    """
    found: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "chunk_id" and isinstance(value, str):
                    found.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    try:
        walk(json.loads(result))
    except (json.JSONDecodeError, TypeError):
        pass
    if not found:
        # O resultado pode ter sido truncado (JSON inválido) ou ser texto livre.
        found = CHUNK_ID_RE.findall(result or "")
    return found


def _assistant_message_to_dict(msg: Any) -> dict:
    """Converte a mensagem devolvida pelo SDK (objeto pydantic) no dict que a API espera de volta.

    A API é *stateless*: a cada chamada reenviamos a conversa inteira. A mensagem do
    assistente que pediu ferramentas precisa voltar no histórico, com os mesmos ids
    das tool_calls, senão a API rejeita as mensagens role="tool" seguintes.
    """
    out: dict = {"role": "assistant", "content": msg.content}
    tool_calls = getattr(msg, "tool_calls", None) or []
    if tool_calls:
        out["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in tool_calls
        ]
    return out


def _preview(text: str, limit: int = 200) -> str:
    text = " ".join((text or "").split())  # colapsa quebras de linha para caber numa linha
    return text if len(text) <= limit else text[:limit] + "…"


def run_agent(
    question: str,
    store,
    llm,
    max_steps: int = 8,
    verbose: bool = False,
    console: Console | None = None,
    toolbox=None,
    tool_schemas: list[dict] | None = None,
    extra_instructions: str | None = None,
    check_final: Callable[[str, list[dict]], str | None] | None = None,
) -> Answer:
    """Responde `question` deixando o LLM decidir quais ferramentas usar.

    `toolbox` e `tool_schemas` são opcionais: em produção são criados a partir do
    `store` e do `llm`; nos testes injetamos versões falsas (sem rede).

    Ganchos usados pelo modo híbrido (`hybrid.py`):
    - `extra_instructions`: texto anexado ao prompt de sistema (ex.: "comece pelo grep");
    - `check_final(rascunho, mensagens)`: chamado quando o modelo quer parar. Se devolver
      um texto, ele volta ao modelo como pedido para continuar buscando. Roda no máximo
      uma vez por pergunta e só se ainda houver passos, para não virar um loop.
    """
    if toolbox is None or tool_schemas is None:
        # Import tardio: só precisamos de tools.py quando não há fakes injetados.
        from .tools import TOOL_SCHEMAS, ToolBox

        toolbox = toolbox or ToolBox(store, llm)
        tool_schemas = tool_schemas or TOOL_SCHEMAS

    console = console or Console()
    # O LLMClient acumula uso desde que foi criado; tiramos uma "foto" agora para,
    # no fim, medir só o que ESTA pergunta consumiu.
    usage_before = llm.usage.snapshot()

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT + (f"\n\n{extra_instructions}" if extra_instructions else "")},
        {"role": "user", "content": question},
    ]
    sources: list[str] = []
    trace: list[dict] = []
    final_text: str | None = None
    checked = False

    if verbose:
        console.print(Panel(question, title="[bold cyan]Pergunta[/]", border_style="cyan"))

    for step in range(1, max_steps + 1):
        # ---------- PENSAR ----------
        # O modelo vê o histórico inteiro + a lista de ferramentas e decide o próximo passo.
        msg = llm.chat(messages, tools=tool_schemas)
        tool_calls = getattr(msg, "tool_calls", None) or []

        # Sem tool_calls = o modelo considera que já pode responder. Fim do loop.
        if not tool_calls:
            if check_final and not checked and step < max_steps:
                checked = True
                feedback = check_final(msg.content or "", messages)
                if feedback:
                    # O rascunho fica no histórico, seguido do pedido para continuar.
                    messages.append({"role": "assistant", "content": msg.content or ""})
                    messages.append({"role": "user", "content": feedback})
                    trace.append({"step": step, "tool": "check_final", "args": {},
                                  "result_preview": _preview(feedback)})
                    if verbose:
                        console.print(f"[bold magenta]Passo {step}:[/] verificador pediu mais buscas")
                    continue
            final_text = msg.content or ""
            if verbose:
                console.print(f"[bold green]Passo {step}:[/] resposta final (sem ferramentas)")
            break

        # Guardamos no histórico o pedido do assistente (com os ids das chamadas).
        messages.append(_assistant_message_to_dict(msg))
        if verbose and msg.content:
            # Alguns modelos "pensam em voz alta" junto com as tool_calls.
            console.print(f"[dim]Passo {step} — raciocínio: {_preview(msg.content, 300)}[/]")

        # ---------- AGIR ----------
        # Executamos TODAS as chamadas pedidas neste passo (o modelo pode pedir várias
        # buscas independentes de uma vez — isso economiza rodadas).
        for tc in tool_calls:
            name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
                if not isinstance(args, dict):
                    raise ValueError("argumentos devem ser um objeto JSON")
            except (json.JSONDecodeError, ValueError) as exc:
                # Não derrubamos o loop: devolvemos o erro ao modelo para ele se corrigir.
                args = {}
                result = f"ERRO: argumentos inválidos para '{name}' ({exc}): {raw_args[:200]}"
            else:
                result = toolbox.call(name, args)

            # ---------- OBSERVAR ----------
            # O resultado volta como mensagem role="tool" ligada à chamada pelo tool_call_id.
            messages.append({"role": "tool", "tool_call_id": tc.id, "name": name, "content": result})

            for cid in _collect_chunk_ids(result):
                if cid not in sources:
                    sources.append(cid)
            trace.append({"step": step, "tool": name, "args": args, "result_preview": _preview(result)})

            if verbose:
                console.print(
                    f"[bold yellow]Passo {step}[/] → [bold]{name}[/]"
                    f"({json.dumps(args, ensure_ascii=False)})\n   [dim]{_preview(result, 160)}[/]"
                )

    if final_text is None:
        # Estourou max_steps sem o modelo concluir. Em vez de devolver nada, pedimos
        # uma última resposta SEM ferramentas (tools=None obriga a responder em texto).
        if verbose:
            console.print(f"[bold red]Limite de {max_steps} passos atingido — forçando resposta final[/]")
        messages.append({"role": "user", "content": FORCE_FINAL_PROMPT})
        msg = llm.chat(messages, tools=None)
        final_text = msg.content or f"{NOT_FOUND}."
        trace.append({"step": max_steps + 1, "tool": None, "args": {}, "result_preview": "resposta forçada"})

    # read_page devolve texto puro (sem chunk_id); o ToolBox real registra esses chunks em seen_chunks.
    for cid in getattr(toolbox, "seen_chunks", []):
        if cid not in sources:
            sources.append(cid)

    return Answer(text=final_text, sources=sources, usage=llm.usage.since(usage_before), trace=trace)
