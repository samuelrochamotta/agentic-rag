"""Cliente fino sobre a API do OpenRouter (compatível com a API da OpenAI).

Além de chamar o modelo, contabiliza uso (chamadas, tokens, custo e latência) —
é isso que permite comparar o custo do RAG simples com o do agêntico.
"""

import time
from dataclasses import dataclass, field

import numpy as np
from openai import OpenAI

from .config import settings


@dataclass
class Usage:
    llm_calls: int = 0
    embed_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    latency_s: float = 0.0
    decider_calls: int = 0  # decisões tipadas do modo híbrido (Jev ou LLM)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def add(self, other: "Usage") -> None:
        for f in self.__dataclass_fields__:
            setattr(self, f, getattr(self, f) + getattr(other, f))

    def snapshot(self) -> "Usage":
        return Usage(**{k: getattr(self, k) for k in self.__dataclass_fields__})

    def since(self, before: "Usage") -> "Usage":
        """Diferença entre o uso atual e um snapshot anterior."""
        return Usage(**{k: getattr(self, k) - getattr(before, k) for k in self.__dataclass_fields__})


@dataclass
class Answer:
    text: str
    sources: list[str]
    usage: Usage
    trace: list[dict] = field(default_factory=list)


class LLMClient:
    def __init__(self, chat_model: str | None = None, embed_model: str | None = None):
        if not settings.api_key:
            raise RuntimeError("Defina OPENROUTER_API_KEY no arquivo .env")
        self.client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
        self.chat_model = chat_model or settings.chat_model
        self.embed_model = embed_model or settings.embed_model
        self.usage = Usage()  # acumulado desde a criação do cliente

    def chat(self, messages: list[dict], tools: list[dict] | None = None, temperature: float = 0.0,
             response_format: dict | None = None):
        """Chama o modelo de chat e devolve a `message` da primeira escolha."""
        kwargs = {"model": self.chat_model, "messages": messages, "temperature": temperature}
        if tools:
            kwargs["tools"] = tools
        if response_format:
            kwargs["response_format"] = response_format
        t0 = time.perf_counter()
        resp = self.client.chat.completions.create(**kwargs)
        self.usage.latency_s += time.perf_counter() - t0
        self.usage.llm_calls += 1
        if resp.usage:
            self.usage.prompt_tokens += resp.usage.prompt_tokens or 0
            self.usage.completion_tokens += resp.usage.completion_tokens or 0
            self.usage.cost_usd += getattr(resp.usage, "cost", None) or 0.0  # campo extra do OpenRouter
        return resp.choices[0].message

    def embed(self, texts: list[str], batch_size: int = 100) -> np.ndarray:
        """Gera embeddings normalizados (norma L2 = 1), então produto escalar = cosseno."""
        vectors: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            t0 = time.perf_counter()
            resp = self.client.embeddings.create(model=self.embed_model, input=batch)
            self.usage.latency_s += time.perf_counter() - t0
            self.usage.embed_calls += 1
            if resp.usage:
                self.usage.prompt_tokens += resp.usage.prompt_tokens or 0
                self.usage.cost_usd += getattr(resp.usage, "cost", None) or 0.0
            vectors.extend(d.embedding for d in sorted(resp.data, key=lambda d: d.index))
        arr = np.asarray(vectors, dtype=np.float32)
        return arr / np.linalg.norm(arr, axis=1, keepdims=True).clip(min=1e-12)
