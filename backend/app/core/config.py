from __future__ import annotations

import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """
    Project structure:

    rag-assistant-project/
    ├── backend/
    │   └── app/
    │       └── core/
    │           └── config.py
    ├── data/
    │   └── vector_store/
    └── notebooks/
    """
    return Path(__file__).resolve().parents[3]


PROJECT_ROOT = get_project_root()

VECTOR_STORE_DIR = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "vector_store"
)

PHASE2_CONFIG_PATH = VECTOR_STORE_DIR / "config.json"


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    ollama_model: str | None = None
    top_k: int | None = None

    cors_allow_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_allow_origins.split(",")
            if origin.strip()
        ]


def load_phase2_config() -> dict:
    if not PHASE2_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Phase 2 config not found: {PHASE2_CONFIG_PATH}"
        )

    with PHASE2_CONFIG_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        config = json.load(file)

    required_fields = [
        "embedding_model",
        "embedding_dim",
        "collection_name",
    ]

    missing = [
        field
        for field in required_fields
        if field not in config
    ]

    if missing:
        raise ValueError(
            f"Phase 2 config is missing required fields: {missing}"
        )

    return config


def get_embedding_model_name(
    phase2_config: dict,
) -> str:
    return phase2_config["embedding_model"]


def get_collection_name(
    phase2_config: dict,
) -> str:
    return phase2_config["collection_name"]


def get_top_k(
    settings: Settings,
    phase2_config: dict,
) -> int:
    if settings.top_k is not None:
        return settings.top_k

    return int(
        phase2_config.get(
            "top_k_default",
            5,
        )
    )


def get_ollama_model(
    settings: Settings,
    phase2_config: dict,
) -> str:
    if settings.ollama_model:
        return settings.ollama_model

    phase2_model = phase2_config.get(
        "ollama_model_used"
    )

    if phase2_model:
        return phase2_model

    raise ValueError(
        "No Ollama model configured. "
        "Set OLLAMA_MODEL in .env or provide "
        "'ollama_model_used' in Phase 2 config.json."
    )