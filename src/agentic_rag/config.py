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
    chat_model: str = os.getenv("CHAT_MODEL", "openai/gpt-4.1-mini")
    embed_model: str = os.getenv("EMBED_MODEL", "openai/text-embedding-3-small")
    index_dir: Path = Path(os.getenv("INDEX_DIR", ".index"))


settings = Settings()
