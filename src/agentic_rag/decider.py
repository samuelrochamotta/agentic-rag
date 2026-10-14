"""Decisões tipadas: perguntas fechadas (escolha entre opções, sim/não) com confiança.

O LLM do agente é ótimo para *gerar* texto, mas várias decisões da arquitetura são
discretas: "essa pergunta é simples ou precisa do agente?", "a evidência já basta?".
Para elas não queremos texto livre; queremos uma resposta de um tipo conhecido e um
número de confiança para comparar com um limiar.

Este módulo define uma interface pequena (`Decider`) com duas implementações:

- `JevDecider`: chama o Jev, da TypeSafe AI (https://docs.typesafe.ai/api), pelo
  OpenRouter (`POST /api/v1/systemone`, mesma chave dos outros modelos). Não é um LLM:
  recebe um "estado" + perguntas tipadas e devolve as respostas numa passada só, com
  probabilidades por opção. Não passa pelo SDK da OpenAI porque não é chat completions.
- `LLMDecider`: faz a mesma coisa com o LLM de chat e `response_format` (JSON schema).
  É a linha de base: sem ela não dá para saber se o Jev ajuda ou se qualquer saída
  estruturada já bastaria. A confiança aqui é *autodeclarada* pelo modelo, o que
  costuma ser mal calibrado.

Os dois recebem o `llm` de quem os chama e registram o uso em `llm.usage`. Assim o
custo das decisões entra na conta do sistema híbrido, e cada thread da avaliação
continua com o seu próprio contador.
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Protocol

from .config import settings


# ---------------------------------------------------------------------------
# Perguntas e respostas tipadas
# ---------------------------------------------------------------------------

@dataclass
class Choice:
    """Escolha UMA opção. `options` mapeia cada opção para a descrição do que ela significa."""

    instructions: str
    options: dict[str, str | None]


@dataclass
class Noul:
    """Pergunta de sim/não (o Jev chama esse tipo de "noul"). Os critérios são opcionais."""

    instructions: str
    if_true: str | None = None
    if_false: str | None = None


Question = Choice | Noul


@dataclass
class Decision:
    """Resposta tipada. `value` é a opção escolhida (Choice) ou um bool (Noul)."""

    value: str | bool
    confidence: float  # 0 a 1
    probabilities: dict[str, float] = field(default_factory=dict)


class Decider(Protocol):
    name: str

    def decide(self, state: str | dict, questions: dict[str, Question], llm) -> dict[str, Decision]: ...


# ---------------------------------------------------------------------------
# Jev (TypeSafe AI)
# ---------------------------------------------------------------------------

class DeciderError(RuntimeError):
    pass


def _jev_question(q: Question) -> dict:
    """Converte nossa pergunta no formato da API: {type, instructions, criteria}."""
    if isinstance(q, Choice):
        return {"type": "choice", "instructions": q.instructions, "criteria": q.options}
    out: dict = {"type": "noul", "instructions": q.instructions}
    if q.if_true or q.if_false:
        out["criteria"] = {"true": q.if_true, "false": q.if_false}
    return out


def _jev_answer(q: Question, raw: dict) -> Decision:
    if isinstance(q, Choice):
        return Decision(value=raw["choice"], confidence=float(raw.get("confidence", 0.0)),
                        probabilities={k: float(v) for k, v in (raw.get("probabilities") or {}).items()})
    # Noul devolve só a probabilidade de "sim" (0 a 1), sem campo de confiança.
    p_yes = float(raw["noul"])
    return Decision(value=p_yes >= 0.5, confidence=max(p_yes, 1 - p_yes),
                    probabilities={"true": p_yes, "false": 1 - p_yes})


def _urllib_post(url: str, headers: dict, body: dict, timeout: float) -> tuple[int, dict | str]:
    """POST JSON com a biblioteca padrão. Devolve (status, corpo como dict ou texto)."""
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status, raw = resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read().decode("utf-8", errors="replace")
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw


class JevDecider:
    name = "jev"
    # 429 = rate limit, 502 = falha do provedor (o OpenRouter não cobra), 529 = sobrecarga do Jev.
    RETRY_STATUS = (429, 502, 529)

    def __init__(self, api_key: str | None = None, model: str | None = None, base_url: str | None = None,
                 post: Callable = _urllib_post, sleep: Callable[[float], None] = time.sleep,
                 max_retries: int = 3, timeout: float = 30.0):
        self.api_key = api_key or settings.api_key
        if not self.api_key:
            raise RuntimeError("Defina OPENROUTER_API_KEY no arquivo .env")
        self.model = model or settings.jev_model
        self.url = (base_url or settings.base_url).rstrip("/") + "/systemone"
        self.post, self.sleep = post, sleep
        self.max_retries, self.timeout = max_retries, timeout
        self.cost_missing = False  # vira True se alguma resposta vier sem usage.cost

    def decide(self, state, questions, llm) -> dict[str, Decision]:
        body = {"model": self.model, "state": state,
                "questions": {qid: _jev_question(q) for qid, q in questions.items()}}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        t0 = time.perf_counter()
        for attempt in range(self.max_retries + 1):
            status, data = self.post(self.url, headers, body, self.timeout)
            if status not in self.RETRY_STATUS or attempt == self.max_retries:
                break
            self.sleep(2 ** attempt)
        llm.usage.latency_s += time.perf_counter() - t0
        llm.usage.decider_calls += 1

        if status != 200 or not isinstance(data, dict):
            # Em 422 o corpo diz qual campo está errado: é o que mais ajuda a depurar.
            raise DeciderError(f"Jev respondeu HTTP {status}: {str(data)[:500]}")
        # O OpenRouter devolve o custo em US$ (a API nativa da TypeSafe não devolve).
        cost = (data.get("usage") or {}).get("cost")
        if cost is None:
            self.cost_missing = True
        llm.usage.cost_usd += cost or 0.0

        answers = data.get("answers") or {}
        return {qid: _jev_answer(q, answers[qid]) for qid, q in questions.items()}


# ---------------------------------------------------------------------------
# Linha de base: o próprio LLM com saída estruturada
# ---------------------------------------------------------------------------

LLM_DECIDER_PROMPT = """Você responde perguntas fechadas sobre um ESTADO (texto ou JSON).
Para cada pergunta, escolha uma das opções permitidas e informe sua confiança de 0 a 1
(1 = certeza absoluta). Responda SOMENTE com o JSON pedido."""


def _llm_schema(questions: dict[str, Question]) -> dict:
    props = {}
    for qid, q in questions.items():
        value = ({"type": "string", "enum": list(q.options)} if isinstance(q, Choice) else {"type": "boolean"})
        props[qid] = {"type": "object", "additionalProperties": False, "required": ["value", "confidence"],
                      "properties": {"value": value, "confidence": {"type": "number"}}}
    return {"type": "object", "additionalProperties": False, "required": list(questions), "properties": props}


def _describe(qid: str, q: Question) -> str:
    if isinstance(q, Choice):
        opts = "\n".join(f'  - "{k}": {v or ""}' for k, v in q.options.items())
        return f"[{qid}] (escolha uma opção) {q.instructions}\n{opts}"
    extra = "".join(f"\n  - {label}: {text}" for label, text in (("true", q.if_true), ("false", q.if_false)) if text)
    return f"[{qid}] (true/false) {q.instructions}{extra}"


def _parse_llm_json(raw: str) -> dict:
    for candidate in (raw or "", *re.findall(r"\{.*\}", raw or "", flags=re.DOTALL)):
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
    raise DeciderError(f"não foi possível interpretar a decisão do LLM: {(raw or '')[:200]}")


class LLMDecider:
    name = "llm"

    def decide(self, state, questions, llm) -> dict[str, Decision]:
        state_text = state if isinstance(state, str) else json.dumps(state, ensure_ascii=False, indent=1)
        listing = "\n\n".join(_describe(qid, q) for qid, q in questions.items())
        messages = [
            {"role": "system", "content": LLM_DECIDER_PROMPT},
            {"role": "user", "content": f"ESTADO:\n{state_text}\n\nPERGUNTAS:\n{listing}\n\n"
                                        'Formato: {"<id>": {"value": ..., "confidence": 0.0-1.0}, ...}'},
        ]
        fmt = {"type": "json_schema", "json_schema": {"name": "decisoes", "strict": True,
                                                      "schema": _llm_schema(questions)}}
        try:
            msg = llm.chat(messages, response_format=fmt)
        except Exception:
            # Mesmo padrão do juiz: nem todo provedor do OpenRouter aceita response_format.
            msg = llm.chat(messages)
        llm.usage.decider_calls += 1
        data = _parse_llm_json(msg.content or "")

        out: dict[str, Decision] = {}
        for qid, q in questions.items():
            item = data.get(qid) or {}
            conf = min(max(float(item.get("confidence", 0.0)), 0.0), 1.0)
            value = item.get("value")
            if isinstance(q, Choice):
                if value not in q.options:  # opção inválida: confiança zero, quem chama cai no caminho seguro
                    value, conf = next(iter(q.options)), 0.0
            else:
                value = value if isinstance(value, bool) else str(value).strip().lower() in ("true", "sim", "yes")
            out[qid] = Decision(value=value, confidence=conf)
        return out


def make_decider(kind: str | None = None) -> Decider:
    """`jev` (padrão) ou `llm`."""
    kind = kind or "jev"
    if kind == "jev":
        return JevDecider()
    if kind == "llm":
        return LLMDecider()
    raise ValueError(f"decider desconhecido: {kind}")
