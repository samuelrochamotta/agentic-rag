"""RAG híbrido: decisões tipadas (Jev ou LLM) em volta do RAG simples e do agêntico.

A avaliação mostrou que o agêntico custa ~3,3× mais e só ganha em alguns tipos de
pergunta. A ideia aqui é gastar o agente só onde ele faz diferença:

    pergunta ─► ROTEADOR (Choice) ──"simples" com confiança alta──► RAG simples
                      │
                      └─ qualquer outro caso ─► RAG agêntico + dica da 1ª ferramenta
                                                     │
                                  quando ele quer parar: VERIFICADOR (Noul)
                                  "a evidência sustenta a resposta?"
                                  não → manda buscar mais uma vez

O roteador só vê a pergunta, não o documento. Por isso ele classifica pela FORMA da
pergunta; "distrator" e "sem_resposta" dependem do conteúdo do documento e não
aparecem aqui. Na dúvida, a pergunta vai para o agente: errar para o lado caro
custa dinheiro, errar para o lado barato custa a resposta.
"""

from __future__ import annotations

from .agent import run_agent
from .config import settings
from .decider import Choice, Decider, Noul
from .evaluate import declares_not_found
from .llm import Answer
from .simple_rag import run_simple

ROUTE = Choice(
    instructions="Classifique a pergunta do usuário, feita sobre um documento corporativo, pelo tipo de busca "
                 "que ela exige. Se ela se encaixar em mais de um tipo, escolha o mais difícil.",
    options={
        "simples": "Pede um único fato direto (um número, prazo, nome ou data), que provavelmente está "
                   "escrito num só trecho do documento.",
        "multi_hop": "Precisa encadear informações: a resposta de uma parte é necessária para buscar a outra "
                     "(ex.: 'o orçamento da unidade gerida por Fulano').",
        "codigo_exato": "Gira em torno de um código, sigla ou identificador exato (ex.: ACX-7741, Anexo C-3).",
        "agregacao": "Pede para contar, somar, listar ou comparar itens que podem estar espalhados "
                     "pelo documento.",
        "referencia_secao": "Cita uma seção, capítulo ou página pelo número (ex.: 'o que diz a seção 7.3?').",
    },
)

# Dica anexada ao prompt do agente para cada tipo de pergunta.
HINTS = {
    "multi_hop": "Dica: esta pergunta parece exigir várias etapas. Encontre primeiro o elo intermediário "
                 "(nome, unidade, código) e só então busque a informação final.",
    "codigo_exato": "Dica: esta pergunta gira em torno de um código exato. Comece por search_keyword ou grep "
                    "e confira se o código encontrado é idêntico ao da pergunta.",
    "agregacao": "Dica: esta pergunta pede contagem, soma ou lista. Use grep para enumerar TODAS as "
                 "ocorrências (a busca top-k corta resultados) e calculator para as contas.",
    "referencia_secao": "Dica: esta pergunta cita uma seção ou página. Comece por list_outline e depois "
                        "use read_page.",
}

EVIDENCE = Noul(
    instructions="O ESTADO traz uma pergunta, um rascunho de resposta e as evidências encontradas nas buscas. "
                 "As evidências sustentam TODAS as afirmações do rascunho e cobrem TODAS as partes da pergunta? "
                 "Em contagens e somas, as evidências mostram que todas as ocorrências foram enumeradas?",
    if_true="Cada afirmação e cada parte da pergunta tem apoio nas evidências.",
    if_false="Falta evidência para alguma afirmação, parte da pergunta ou ocorrência.",
)

MORE_SEARCH = (
    "Um verificador indicou que as evidências podem não sustentar toda a resposta. Antes de responder, "
    "faça buscas adicionais: confira cada parte da pergunta, use grep para enumerar todas as ocorrências "
    "em contagens e somas, e verifique se os trechos são da versão vigente. Depois responda de novo."
)

MAX_EVIDENCE_CHARS = 12000


def _evidence(messages: list[dict]) -> str:
    """Junta os resultados das ferramentas (mensagens role="tool") num texto só."""
    text = "\n\n".join(f"[{m.get('name')}] {m['content']}" for m in messages if m.get("role") == "tool")
    return text[-MAX_EVIDENCE_CHARS:]  # se passar do limite, ficam as buscas mais recentes


def run_hybrid(
    question: str,
    store,
    llm,
    decider: Decider,
    max_steps: int = 8,
    route_threshold: float | None = None,
    evidence_threshold: float | None = None,
    verify: bool = True,
    **agent_kwargs,
) -> Answer:
    route_threshold = settings.route_threshold if route_threshold is None else route_threshold
    evidence_threshold = settings.evidence_threshold if evidence_threshold is None else evidence_threshold
    usage_before = llm.usage.snapshot()  # inclui o custo das decisões, não só o do RAG escolhido

    route = decider.decide(question, {"route": ROUTE}, llm)["route"]
    go_simple = route.value == "simples" and route.confidence >= route_threshold
    route_entry = {"step": 0, "tool": f"router:{decider.name}",
                   "args": {"categoria": route.value, "confianca": round(route.confidence, 3)},
                   "result_preview": "RAG simples" if go_simple else "RAG agêntico"}

    if go_simple:
        answer = run_simple(question, store, llm)
    else:
        def check_final(draft: str, messages: list[dict]) -> str | None:
            # "Não encontrei" é uma resposta legítima (categoria sem_resposta). Perguntar se a
            # evidência a sustenta daria "não" sempre e gastaria um passo à toa.
            if declares_not_found(draft):
                return None
            state = {"pergunta": question, "rascunho": draft, "evidencias": _evidence(messages)}
            ok = decider.decide(state, {"evidence": EVIDENCE}, llm)["evidence"]
            p_yes = ok.probabilities.get("true", ok.confidence if ok.value else 1 - ok.confidence)
            return MORE_SEARCH if p_yes < evidence_threshold else None

        answer = run_agent(question, store, llm, max_steps=max_steps,
                           extra_instructions=HINTS.get(route.value),
                           check_final=check_final if verify else None, **agent_kwargs)

    answer.trace = [route_entry, *answer.trace]
    answer.usage = llm.usage.since(usage_before)
    return answer


def describe_route(answer: Answer) -> str:
    """Linha curta para a CLI: 'router:jev → agregacao (0.93) → RAG agêntico'."""
    first = answer.trace[0] if answer.trace else {}
    if not str(first.get("tool", "")).startswith("router"):
        return ""
    args = first["args"]
    return f"{first['tool']} → {args['categoria']} ({args['confianca']}) → {first['result_preview']}"

