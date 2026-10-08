"""Testes OFFLINE do loop agêntico e das checagens do avaliador.

Nada aqui acessa a rede: o LLM é um roteiro de respostas pré-definidas e o
ToolBox é um fake que só registra as chamadas. Assim testamos a *mecânica* do
loop (pensar → agir → observar) sem depender do modelo.
"""

import copy
import json
from types import SimpleNamespace

from agentic_rag.agent import run_agent
from agentic_rag.evaluate import _parse_judge_json, declares_not_found, missing_terms, must_contain_ok, normalize
from agentic_rag.llm import Usage


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

def tool_call(id_, name, args):
    """Imita o objeto tool_call do SDK da OpenAI (arguments é uma STRING JSON)."""
    arguments = args if isinstance(args, str) else json.dumps(args)
    return SimpleNamespace(id=id_, type="function", function=SimpleNamespace(name=name, arguments=arguments))


def assistant(content=None, tool_calls=None):
    return SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls)


class FakeLLM:
    """Devolve as mensagens do roteiro em ordem; quando acaba, repete a última."""

    def __init__(self, script):
        self.script = list(script)
        self.usage = Usage()
        self.calls = []  # (cópia das mensagens, tools) de cada chamada

    def chat(self, messages, tools=None, **kwargs):
        self.calls.append((copy.deepcopy(messages), tools))
        self.usage.llm_calls += 1
        self.usage.prompt_tokens += 10
        self.usage.completion_tokens += 5
        idx = min(len(self.calls) - 1, len(self.script) - 1)
        return self.script[idx]


class FakeToolBox:
    def __init__(self):
        self.calls = []

    def call(self, name, args):
        self.calls.append((name, args))
        page = args.get("page", 1)
        return json.dumps([{"chunk_id": f"manual:p{page}:c0", "page": page, "section": None, "text": f"{name} ok"}])


SCHEMAS = [{"type": "function", "function": {"name": "search_keyword", "parameters": {}}}]


# ---------------------------------------------------------------------------
# Loop agêntico
# ---------------------------------------------------------------------------

def test_executa_varias_tools_no_mesmo_passo_e_responde():
    llm = FakeLLM([
        assistant(tool_calls=[
            tool_call("call_1", "search_keyword", {"query": "ACX-7741"}),
            tool_call("call_2", "read_page", {"doc_id": "manual", "page": 3}),
        ]),
        assistant(content="O código é ACX-7741 [p. 3]."),
    ])
    tb = FakeToolBox()
    # Usage acumulado anterior não pode vazar para o Answer (usamos since(snapshot)).
    llm.usage.llm_calls = 7

    ans = run_agent("Qual o código?", store=None, llm=llm, toolbox=tb, tool_schemas=SCHEMAS)

    assert ans.text == "O código é ACX-7741 [p. 3]."
    assert tb.calls == [("search_keyword", {"query": "ACX-7741"}), ("read_page", {"doc_id": "manual", "page": 3})]
    assert ans.usage.llm_calls == 2
    assert ans.usage.total_tokens == 30
    assert ans.sources == ["manual:p1:c0", "manual:p3:c0"]
    assert [t["tool"] for t in ans.trace] == ["search_keyword", "read_page"]
    assert all(t["step"] == 1 for t in ans.trace)

    # Na 2ª chamada o histórico deve ter: system, user, assistant(tool_calls), tool, tool.
    messages, tools = llm.calls[1]
    assert tools == SCHEMAS
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "tool", "tool"]
    asst = messages[2]
    assert [tc["id"] for tc in asst["tool_calls"]] == ["call_1", "call_2"]
    assert asst["tool_calls"][0]["function"]["name"] == "search_keyword"
    assert isinstance(asst["tool_calls"][0]["function"]["arguments"], str)
    assert messages[3]["tool_call_id"] == "call_1"
    assert messages[4]["tool_call_id"] == "call_2"


def test_respeita_max_steps_e_forca_resposta_sem_tools():
    # O roteiro só pede ferramentas; a última chamada (forçada) devolve o mesmo
    # objeto, então damos a ele um conteúdo para servir de resposta final.
    looping = assistant(content="resposta parcial", tool_calls=[tool_call("c", "search_keyword", {"query": "x"})])
    final = assistant(content="Melhor resposta possível [p. 1].")

    class LLM(FakeLLM):
        def chat(self, messages, tools=None, **kw):
            super().chat(messages, tools, **kw)
            return final if tools is None else looping

    llm = LLM([looping])
    tb = FakeToolBox()
    ans = run_agent("pergunta", store=None, llm=llm, max_steps=2, toolbox=tb, tool_schemas=SCHEMAS)

    assert len(llm.calls) == 3          # 2 passos com tools + 1 chamada final
    assert llm.calls[-1][1] is None     # a última foi SEM ferramentas
    assert llm.calls[-1][0][-1]["role"] == "user"  # com o pedido de resposta final
    assert len(tb.calls) == 2
    assert ans.text == "Melhor resposta possível [p. 1]."
    assert ans.usage.llm_calls == 3


def test_argumentos_invalidos_viram_erro_e_loop_continua():
    llm = FakeLLM([
        assistant(tool_calls=[tool_call("bad", "search_keyword", "{isto não é json")]),
        assistant(content="Não encontrei essa informação no documento."),
    ])
    tb = FakeToolBox()
    ans = run_agent("?", store=None, llm=llm, toolbox=tb, tool_schemas=SCHEMAS)

    assert tb.calls == []  # a tool não foi executada
    tool_msg = llm.calls[1][0][-1]
    assert tool_msg["role"] == "tool" and tool_msg["tool_call_id"] == "bad"
    assert tool_msg["content"].startswith("ERRO")
    assert ans.text.startswith("Não encontrei")


def test_resposta_direta_sem_tools():
    llm = FakeLLM([assistant(content="Resposta [p. 2].")])
    ans = run_agent("?", store=None, llm=llm, toolbox=FakeToolBox(), tool_schemas=SCHEMAS)
    assert ans.text == "Resposta [p. 2]." and ans.sources == [] and ans.trace == []
    assert ans.usage.llm_calls == 1


# ---------------------------------------------------------------------------
# Checagens do avaliador
# ---------------------------------------------------------------------------

def test_normalize_remove_acentos_e_caixa():
    assert normalize("  Política de REEMBOLSO   Vigente ") == "politica de reembolso vigente"


def test_must_contain_ignora_acentos_e_maiusculas():
    resposta = "O prazo de reembolso é de 30 DIAS úteis conforme a Política v2 [p. 4]."
    assert must_contain_ok(resposta, ["30 dias", "politica v2"])
    assert must_contain_ok(resposta, ["Útéis"])
    assert must_contain_ok(resposta, [])
    assert must_contain_ok(resposta, None)
    assert not must_contain_ok(resposta, ["30 dias", "60 dias"])
    assert missing_terms(resposta, ["30 dias", "60 dias"]) == ["60 dias"]


def test_declares_not_found():
    assert declares_not_found("Não encontrei essa informação no documento.")
    assert declares_not_found("NAO ENCONTREI isso.")
    assert declares_not_found("Essa informação não está presente no documento.")
    assert not declares_not_found("O prazo é de 30 dias [p. 4].")


def test_parse_do_juiz_e_robusto():
    assert _parse_judge_json('{"correct": true, "reason": "ok"}') == {"correct": True, "reason": "ok"}
    cercado = 'Segue:\n```json\n{"correct": false, "reason": "valor antigo"}\n```'
    assert _parse_judge_json(cercado) == {"correct": False, "reason": "valor antigo"}
    assert _parse_judge_json("sem json nenhum")["correct"] is False
