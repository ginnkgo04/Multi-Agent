from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.schemas import KnowledgeIngestRequest
from app.services.context_document_service import ContextDocumentService


class RagService:
    def __init__(self, context_documents: ContextDocumentService | None = None) -> None:
        self.context_documents = context_documents or ContextDocumentService()

    async def ingest(self, session: Session, payload: KnowledgeIngestRequest, embedding_provider) -> int:
        return await self.context_documents.ingest_external_knowledge(session, payload, embedding_provider)

    async def retrieve(
        self,
        session: Session,
        project_id: str,
        query: str,
        embedding_provider,
        top_k: int | None = None,
        run_id: str | None = None,
        source_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        return await self.context_documents.retrieve(
            session,
            project_id,
            query,
            embedding_provider,
            run_id=run_id,
            top_k=top_k,
            source_types=source_types,
        )

    def get_shared_plan(self, session: Session, run_id: str) -> tuple[str | None, dict[str, Any]]:
        record = self.context_documents.get_current_shared_plan(session, run_id)
        if record is None:
            return None, {}
        return record.id, dict(record.plan_payload or {})

    async def _embed_many(self, embedding_provider, texts: list[str]) -> list[list[float]]:
        return await self.context_documents._embed_many(embedding_provider, texts)

    async def _embed_query(self, embedding_provider, query: str) -> list[float]:
        return await self.context_documents._embed_query(embedding_provider, query)

    @staticmethod
    def _chunk_text(content: str, size: int = 320) -> list[str]:
        return ContextDocumentService._chunk_text(content, size=size)

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        return ContextDocumentService._cosine_similarity(left, right)
