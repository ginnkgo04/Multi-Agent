from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "orchestrator.db"


class Settings(BaseSettings):
    app_name: str = "Multi-Agent Orchestration Platform"
    api_prefix: str = "/api"
    database_url: str = f"sqlite:///{DEFAULT_DATABASE_PATH}"
    app_data_dir: Path = PROJECT_ROOT / "data"
    task_root_dir: Path = PROJECT_ROOT / "tasks"
    api_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    max_cycles: int = 3
    node_retry_limit: int = 2
    default_chat_provider: str = "primary-llm"
    default_embedding_provider: str = "primary-embedding"
    retriever_top_k: int = 4
    context_char_budget: int = 8000
    llm_provider: str = "openai-compatible"
    llm_model: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    embedding_provider: str = "openai-compatible"
    embedding_model: str = ""
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    multi_agent_task_timeout_seconds: int = 900
    terminal_timeout_seconds: int = 120

    model_config = SettingsConfigDict(
        env_file=str(API_ROOT / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.app_data_dir.mkdir(parents=True, exist_ok=True)
    settings.task_root_dir.mkdir(parents=True, exist_ok=True)
    return settings
