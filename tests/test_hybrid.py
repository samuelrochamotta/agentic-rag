"""Testes OFFLINE das decisões tipadas (Jev e LLM) e do modo híbrido.

O Jev é testado com um `post` falso que devolve respostas no formato da documentação
(https://docs.typesafe.ai/api, servida pelo OpenRouter); nada aqui acessa a rede.
"""

import json
from types import SimpleNamespace

import pytest

from agentic_rag.agent import run_agent
from agentic_rag.decider import Choice, Decision, DeciderError, JevDecider, LLMDecider, Noul
from agentic_rag.evaluate import aggregate, render_markdown
from agentic_rag.hybrid import HINTS, MORE_SEARCH, run_hybrid
from agentic_rag.llm import Usage
from test_agent import SCHEMAS, FakeLLM, FakeToolBox, assistant, tool_call

COR = Choice("Qual a cor?", {"azul": "céu", "verde": None})
SIM = Noul("É verdade?", if_true="sim", if_false="não")


class Holder:
    """Só o que os deciders usam do LLMClient: o `usage`."""

    def __init__(self):
        self.usage = Usage()


# ---------------------------------------------------------------------------
# JevDecider
# ---------------------------------------------------------------------------

def jev_ok(answers, cost=0.00003):
    usage = {"input_tokens": 275, "output_tokens": 20}
    if cost is not None:
        usage["cost"] = cost  # campo extra do OpenRouter
    return 200, {"model": "~typesafe/jev-latest", "answers": answers, "usage": usage}


def test_jev_monta_requisicao_e_interpreta_respostas():
    sent = []

    def post(url, headers, body, timeout):
        sent.append((url, headers, body))
        return jev_ok({
            "cor": {"type": "choice", "choice": "verde", "probabilities": {"azul": 0.1, "verde": 0.9},
                    "confidence": 0.85},
            "sim": {"type": "noul", "noul": 0.2},
        })

    holder = Holder()
    jev = JevDecider(api_key="k", model="jev-latest", base_url="https://openrouter.ai/api/v1/", post=post)
    out = jev.decide("estado", {"cor": COR, "sim": SIM}, holder)

    url, headers, body = sent[0]
    assert url == "https://openrouter.ai/api/v1/systemone"
    assert headers["Authorization"] == "Bearer k"
    assert body == {"model": "jev-latest", "state": "estado", "questions": {
        "cor": {"type": "choice", "instructions": "Qual a cor?", "criteria": {"azul": "céu", "verde": None}},
        "sim": {"type": "noul", "instructions": "É verdade?", "criteria": {"true": "sim", "false": "não"}},
    }}
    assert out["cor"] == Decision("verde", 0.85, {"azul": 0.1, "verde": 0.9})
    # Noul não tem confiança na API: derivamos de max(p, 1-p).
    assert out["sim"].value is False and out["sim"].confidence == pytest.approx(0.8)
    assert out["sim"].probabilities["true"] == pytest.approx(0.2)
    assert holder.usage.decider_calls == 1
    assert holder.usage.cost_usd == pytest.approx(0.00003) and not jev.cost_missing
    assert holder.usage.llm_calls == 0  # decisão do Jev não é chamada de LLM


def test_jev_tenta_de_novo_em_429_e_mostra_corpo_do_erro():
    statuses = iter([(429, "calma"), (502, "upstream"), jev_ok({"sim": {"type": "noul", "noul": 0.9}}, cost=None)])
    sleeps = []
    jev = JevDecider(api_key="k", post=lambda *a: next(statuses), sleep=sleeps.append)
    out = jev.decide("s", {"sim": SIM}, Holder())
    assert out["sim"].value is True and sleeps == [1, 2]
    assert jev.cost_missing  # sem usage.cost, o relatório avisa que o custo está subestimado

    bad = JevDecider(api_key="k", post=lambda *a: (422, {"detail": "questions.sim.type inválido"}))
    with pytest.raises(DeciderError, match="422.*questions.sim.type"):
        bad.decide("s", {"sim": SIM}, Holder())


# ---------------------------------------------------------------------------
# LLMDecider (linha de base)
# ---------------------------------------------------------------------------

def test_llm_decider_usa_json_schema_e_valida_opcoes():
    llm = FakeLLM([assistant(content=json.dumps({"cor": {"value": "roxo", "confidence": 0.99},
                                                 "sim": {"value": True, "confidence": 1.7}}))])
    out = LLMDecider().decide({"x": 1}, {"cor": COR, "sim": SIM}, llm)

    assert out["cor"].confidence == 0.0              # opção inexistente → confiança zero
    assert out["sim"] == Decision(True, 1.0)          # confiança limitada a [0, 1]
    assert llm.usage.llm_calls == 1 and llm.usage.decider_calls == 1


def test_llm_decider_tenta_sem_response_format_se_provedor_recusar():
    class Picky(FakeLLM):
        def chat(self, messages, tools=None, **kw):
            if kw.get("response_format"):
                raise RuntimeError("response_format não suportado")
            return super().chat(messages, tools, **kw)

    llm = Picky([assistant(content='Claro: {"cor": {"value": "azul", "confidence": 0.7}}')])
    assert LLMDecider().decide("s", {"cor": COR}, llm)["cor"] == Decision("azul", 0.7)


# ---------------------------------------------------------------------------
# Gancho check_final do agente
# ---------------------------------------------------------------------------

def test_check_final_pede_mais_busca_uma_vez_so():
    llm = FakeLLM([
        assistant(content="São 11 [p. 2]."),
        assistant(tool_calls=[tool_call("c1", "grep", {"pattern": "classe 3"})]),
        assistant(content="São 12 [p. 2]."),
    ])
    drafts = []

    def check(draft, messages):
        drafts.append(draft)
        return "busque mais"

    ans = run_agent("Quantos?", store=None, llm=llm, toolbox=FakeToolBox(), tool_schemas=SCHEMAS,
                    extra_instructions="Dica: use grep.", check_final=check)

    assert ans.text == "São 12 [p. 2]."
    assert drafts == ["São 11 [p. 2]."]  # na segunda vez o verificador não roda
    assert llm.calls[0][0][0]["content"].endswith("Dica: use grep.")
    assert [m["role"] for m in llm.calls[1][0]] == ["system", "user", "assistant", "user"]
    assert [t["tool"] for t in ans.trace] == ["check_final", "grep"]


def test_check_final_nao_roda_no_ultimo_passo():
    llm = FakeLLM([assistant(content="Resposta [p. 1].")])
    called = []
    run_agent("?", store=None, llm=llm, max_steps=1, toolbox=FakeToolBox(), tool_schemas=SCHEMAS,
              check_final=lambda d, m: called.append(d) or "mais")
    assert called == []


# ---------------------------------------------------------------------------
# run_hybrid
# ---------------------------------------------------------------------------

class FakeDecider:
    name = "fake"

    def __init__(self, route, conf, evidence_p=0.9):
        self.route, self.conf, self.evidence_p = route, conf, evidence_p
        self.calls = []

    def decide(self, state, questions, llm):
        self.calls.append(list(questions))
        llm.usage.decider_calls += 1
        if "route" in questions:
            return {"route": Decision(self.route, self.conf)}
        p = self.evidence_p
        return {"evidence": Decision(p >= 0.5, max(p, 1 - p), {"true": p, "false": 1 - p})}


@pytest.fixture
def fake_simple(monkeypatch):
    calls = []

    def run_simple(question, store, llm, k=5):
        calls.append(question)
        llm.usage.llm_calls += 1
        return SimpleNamespace(text="simples [p. 1]", sources=[], usage=Usage(), trace=[])

    monkeypatch.setattr("agentic_rag.hybrid.run_simple", run_simple)
    return calls


def test_pergunta_simples_com_confianca_alta_vai_para_rag_simples(fake_simple):
    llm = FakeLLM([assistant(content="não deveria ser chamado")])
    ans = run_hybrid("Qual a jornada?", None, llm, FakeDecider("simples", 0.95), route_threshold=0.8)
    assert fake_simple == ["Qual a jornada?"] and ans.text == "simples [p. 1]"
    assert ans.trace[0]["tool"] == "router:fake" and ans.trace[0]["result_preview"] == "RAG simples"
    assert ans.usage.decider_calls == 1 and ans.usage.llm_calls == 1


def test_baixa_confianca_ou_outra_categoria_vai_para_o_agente_com_dica(fake_simple):
    for route, conf in (("simples", 0.6), ("agregacao", 0.99)):
        llm = FakeLLM([assistant(content="agente [p. 2]")])
        ans = run_hybrid("?", None, llm, FakeDecider(route, conf), route_threshold=0.8,
                         toolbox=FakeToolBox(), tool_schemas=SCHEMAS)
        assert ans.text == "agente [p. 2]" and ans.trace[0]["result_preview"] == "RAG agêntico"
        system = llm.calls[0][0][0]["content"]
        assert (HINTS["agregacao"] in system) == (route == "agregacao")
    assert fake_simple == []


def test_verificador_manda_buscar_mais_quando_evidencia_fraca():
    llm = FakeLLM([assistant(content="São 11 [p. 2]."), assistant(content="São 12 [p. 2].")])
    dec = FakeDecider("agregacao", 0.9, evidence_p=0.2)
    ans = run_hybrid("Quantos?", None, llm, dec, evidence_threshold=0.5, toolbox=FakeToolBox(),
                     tool_schemas=SCHEMAS)
    assert ans.text == "São 12 [p. 2]."
    assert llm.calls[1][0][-1]["content"] == MORE_SEARCH
    assert dec.calls == [["route"], ["evidence"]]
    assert ans.usage.decider_calls == 2 and ans.usage.llm_calls == 2


def test_verificador_aceita_nao_encontrei_sem_gastar_decisao():
    llm = FakeLLM([assistant(content="Não encontrei essa informação no documento.")])
    dec = FakeDecider("simples", 0.3, evidence_p=0.0)
    ans = run_hybrid("PLR?", None, llm, dec, toolbox=FakeToolBox(), tool_schemas=SCHEMAS)
    assert ans.text.startswith("Não encontrei") and dec.calls == [["route"]]


# ---------------------------------------------------------------------------
# Relatório com subconjunto de sistemas
# ---------------------------------------------------------------------------

def _row(id_, systems):
    usage = {"llm_calls": 1, "embed_calls": 0, "prompt_tokens": 10, "completion_tokens": 5,
             "cost_usd": 0.001, "latency_s": 1.0, "decider_calls": 0}
    trace = [{"step": 0, "tool": "router:jev", "args": {"categoria": "simples", "confianca": 0.9},
              "result_preview": "RAG simples"}]
    row = {"id": id_, "category": "simples", "question": "?"}
    for s in systems:
        row[s] = {"answer": {"text": "x", "sources": [], "usage": usage, "trace": trace},
                  "grade": {"correct": True, "reason": ""}}
    return row


def test_relatorio_funciona_so_com_parte_dos_sistemas():
    rows = [_row("q01", ["simple", "hybrid"])]
    summary = aggregate(rows)
    assert set(summary["TOTAL"]) == {"simple", "hybrid"}
    md = render_markdown(rows, summary, decider="jev", notes=["custo do Jev não contabilizado"])
    assert "híbrido (jev)" in md and "agêntico" not in md
    assert "## Roteamento do híbrido" in md and "> custo do Jev não contabilizado" in md
