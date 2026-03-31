from __future__ import annotations

from pydantic import SecretStr
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import ProviderConfigRecord
from app.models.schemas import ProviderConfig, ProviderKind
from app.providers.chat import OpenAICompatibleChatProvider
from app.providers.embedding import OpenAICompatibleEmbeddingProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self.settings = get_settings()

    def seed_defaults(self, session: Session) -> None:
        self._prune_unsupported_configs(session)
        for config in self._default_configs():
            self.upsert_config(session, config)

    def list_configs(self, session: Session) -> list[ProviderConfig]:
        return [self._to_schema(record) for record in session.scalars(select(ProviderConfigRecord)).all()]

    def upsert_config(self, session: Session, config: ProviderConfig) -> ProviderConfig:
        record = session.scalar(
            select(ProviderConfigRecord).where(
                (ProviderConfigRecord.id == config.id) | (ProviderConfigRecord.name == config.name)
            )
        )
        if record is None:
            record = ProviderConfigRecord(id=config.id)
            session.add(record)
        else:
            record.id = config.id
        record.name = config.name
        record.kind = config.kind.value
        record.provider = self._normalize_provider(config.provider)
        record.model = config.model
        record.base_url = config.base_url
        record.api_key = None
        record.is_default = config.is_default
        record.settings = config.settings
        session.commit()
        session.refresh(record)
        return self._to_schema(record)

    def get_config(self, session: Session, name: str, kind: ProviderKind) -> ProviderConfig:
        record = session.scalar(
            select(ProviderConfigRecord).where(
                ProviderConfigRecord.name == name,
                ProviderConfigRecord.kind == kind.value,
            )
        )
        if record is None:
            raise ValueError(f"Provider '{name}' with kind '{kind.value}' was not found.")
        return self._to_schema(record)

    def resolve_chat_provider(self, session: Session, name: str):
        config = self.get_config(session, name, ProviderKind.CHAT)
        base_url = config.base_url or self._default_base_url(self.settings.llm_provider)
        api_key = self.settings.llm_api_key
        model = config.model or self.settings.llm_model
        if not base_url or not api_key or not model:
            raise ValueError("LLM provider is not fully configured. Check LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL.")
        return config, OpenAICompatibleChatProvider(base_url=base_url, api_key=api_key, model=model)

    def resolve_langchain_chat_model(self, session: Session, name: str):
        config = self.get_config(session, name, ProviderKind.CHAT)
        base_url = config.base_url or self._default_base_url(self.settings.llm_provider)
        api_key = self.settings.llm_api_key
        model = config.model or self.settings.llm_model
        if not base_url or not api_key or not model:
            raise ValueError("LLM provider is not fully configured. Check LLM_BASE_URL, LLM_API_KEY, and LLM_MODEL.")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:  # pragma: no cover - exercised in environments without optional deps
            raise RuntimeError("LangChain chat dependencies are not installed. Install langchain and langchain-openai.") from exc
        return config, ChatOpenAI(
            model=model,
            api_key=SecretStr(api_key),
            base_url=base_url,
            temperature=0.1,
            use_responses_api=False,
            output_version="v0",
        )

    def resolve_embedding_provider(self, session: Session, name: str):
        config = self.get_config(session, name, ProviderKind.EMBEDDING)
        base_url = config.base_url or self._default_base_url(self.settings.embedding_provider)
        api_key = self.settings.embedding_api_key
        model = config.model or self.settings.embedding_model
        if not base_url or not api_key or not model:
            raise ValueError(
                "Embedding provider is not fully configured. Check EMBEDDING_BASE_URL, EMBEDDING_API_KEY, and EMBEDDING_MODEL."
            )
        return config, OpenAICompatibleEmbeddingProvider(base_url=base_url, api_key=api_key, model=model)

    def resolve_langchain_embedding_model(self, session: Session, name: str):
        config = self.get_config(session, name, ProviderKind.EMBEDDING)
        base_url = config.base_url or self._default_base_url(self.settings.embedding_provider)
        api_key = self.settings.embedding_api_key
        model = config.model or self.settings.embedding_model
        if not base_url or not api_key or not model:
            raise ValueError(
                "Embedding provider is not fully configured. Check EMBEDDING_BASE_URL, EMBEDDING_API_KEY, and EMBEDDING_MODEL."
            )
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError as exc:  # pragma: no cover - exercised in environments without optional deps
            raise RuntimeError("LangChain embedding dependencies are not installed. Install langchain and langchain-openai.") from exc
        return config, OpenAIEmbeddings(model=model, api_key=SecretStr(api_key), base_url=base_url)

    def validate(self, config: ProviderConfig) -> tuple[bool, str]:
        base_url = config.base_url or self._default_base_url(config.provider)
        if not base_url:
            return False, "Missing base_url."
        if not config.model:
            return False, "Missing model."
        if config.kind is ProviderKind.CHAT and not self.settings.llm_api_key:
            return False, "Missing LLM_API_KEY in apps/api/.env."
        if config.kind is ProviderKind.EMBEDDING and not self.settings.embedding_api_key:
            return False, "Missing EMBEDDING_API_KEY in apps/api/.env."
        return True, f"Provider '{config.name}' is configured for live API calls."

    def _default_configs(self) -> list[ProviderConfig]:
        return [
            ProviderConfig(
                id="primary-llm-id",
                name=self.settings.default_chat_provider,
                kind=ProviderKind.CHAT,
                provider=self._normalize_provider(self.settings.llm_provider),
                model=self.settings.llm_model,
                base_url=self.settings.llm_base_url or self._default_base_url(self.settings.llm_provider),
                is_default=True,
                settings={"source": "env"},
            ),
            ProviderConfig(
                id="primary-embedding-id",
                name=self.settings.default_embedding_provider,
                kind=ProviderKind.EMBEDDING,
                provider=self._normalize_provider(self.settings.embedding_provider),
                model=self.settings.embedding_model,
                base_url=self.settings.embedding_base_url or self._default_base_url(self.settings.embedding_provider),
                is_default=True,
                settings={"source": "env"},
            ),
        ]

    @staticmethod
    def _normalize_provider(provider: str) -> str:
        normalized = (provider or "openai-compatible").strip().lower()
        if normalized in {"openai", "deepseek", "openai-compatible"}:
            return "openai-compatible"
        return normalized

    @staticmethod
    def _default_base_url(provider: str) -> str | None:
        normalized = (provider or "").strip().lower()
        if normalized in {"openai", "openai-compatible"}:
            return "https://api.openai.com/v1"
        if normalized == "deepseek":
            return "https://api.deepseek.com/v1"
        return None

    @staticmethod
    def _prune_unsupported_configs(session: Session) -> None:
        session.execute(
            delete(ProviderConfigRecord).where(
                ProviderConfigRecord.provider.not_in(("openai-compatible",))
            )
        )
        session.commit()

    @staticmethod
    def _to_schema(record: ProviderConfigRecord) -> ProviderConfig:
        return ProviderConfig(
            id=record.id,
            name=record.name,
            kind=ProviderKind(record.kind),
            provider=record.provider,
            model=record.model,
            base_url=record.base_url,
            api_key=None,
            is_default=record.is_default,
            settings=record.settings or {},
        )
