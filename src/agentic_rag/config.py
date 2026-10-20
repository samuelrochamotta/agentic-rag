"""Configurações lidas do arquivo .env (ou das variáveis de ambiente)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    base_url: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    # Mesmo modelo para os dois RAGs: assim a comparação mede só a estratégia de busca.
    chat_model: str = os.getenv("CHAT_MODEL", "deepseek/deepseek-v4.1-flash")
    embed_model: str = os.getenv("EMBED_MODEL", "openai/text-embedding-3-small")
    # Juiz da avaliação: de propósito, um modelo diferente do CHAT_MODEL. Se o sistema avaliado
    # também fosse o juiz, ele estaria corrigindo a própria prova.
    judge_model: str = os.getenv("JUDGE_MODEL", "openai/gpt-6-luna")
    index_dir: Path = Path(os.getenv("INDEX_DIR", ".index"))
    # Modo híbrido (decisões tipadas). O Jev roda pelo OpenRouter, com a mesma chave e a mesma conta.
    # "jev-latest" vira "~typesafe/jev-latest" no OpenRouter; fixe uma versão (ex.: jev-1.13) para reprodutibilidade.
    jev_model: str = os.getenv("JEV_MODEL", "jev-latest")
    route_threshold: float = float(os.getenv("ROUTE_THRESHOLD", "0.8"))
    evidence_threshold: float = float(os.getenv("EVIDENCE_THRESHOLD", "0.5"))


settings = Settings()
