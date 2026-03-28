from __future__ import annotations

import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import KnowledgeChunkRecord
from app.models.schemas import KnowledgeIngestRequest


class RagService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def ingest(self, session: Session, payload: KnowledgeIngestRequest, embedding_provider) -> int:
        chunks = self._chunk_text(payload.content)
        embeddings = await self._embed_many(embedding_provider, chunks)
        for content, embedding in zip(chunks, embeddings, strict=False):
            session.add(
                KnowledgeChunkRecord(
                    project_id=payload.project_id,
                    source=payload.source,
                    content=content,
                    embedding=embedding,
                    chunk_metadata=payload.metadata,
                )
            )
        session.commit()
        return len(chunks)

    async def retrieve(self, session: Session, project_id: str, query: str, embedding_provider, top_k: int | None = None) -> list[dict[str, Any]]:
        chunks = session.scalars(select(KnowledgeChunkRecord).where(KnowledgeChunkRecord.project_id == project_id)).all()
        if not chunks:
            return []
        query_vector = await self._embed_query(embedding_provider, query)
        scored = []
        for chunk in chunks:
            scored.append((self._cosine_similarity(query_vector, chunk.embedding or []), chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        top_chunks = scored[: (top_k or self.settings.retriever_top_k)]
        return [
            {
                "id": chunk.id,
                "source": chunk.source,
                "content": chunk.content,
                "score": round(score, 4),
                "metadata": chunk.chunk_metadata or {},
            }
            for score, chunk in top_chunks
            if score > 0
        ]

    async def _embed_many(self, embedding_provider, texts: list[str]) -> list[list[float]]:
        if hasattr(embedding_provider, "embed_texts"):
            return await embedding_provider.embed_texts(texts)
        if hasattr(embedding_provider, "aembed_documents"):
            return await embedding_provider.aembed_documents(texts)
        if hasattr(embedding_provider, "embed_documents"):
            return embedding_provider.embed_documents(texts)
        raise TypeError("Embedding provider must expose embed_texts or LangChain document embedding methods.")

    async def _embed_query(self, embedding_provider, query: str) -> list[float]:
        if hasattr(embedding_provider, "embed_texts"):
            return (await embedding_provider.embed_texts([query]))[0]
        if hasattr(embedding_provider, "aembed_query"):
            return await embedding_provider.aembed_query(query)
        if hasattr(embedding_provider, "embed_query"):
            return embedding_provider.embed_query(query)
        raise TypeError("Embedding provider must expose embed_texts or LangChain query embedding methods.")

    @staticmethod
    def _chunk_text(content: str, size: int = 320) -> list[str]:
        normalized = " ".join(content.split())
        return [normalized[index : index + size] for index in range(0, len(normalized), size)] or [normalized]

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        limit = min(len(left), len(right))
        numerator = sum(left[index] * right[index] for index in range(limit))
        left_norm = math.sqrt(sum(value * value for value in left[:limit]))
        right_norm = math.sqrt(sum(value * value for value in right[:limit]))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)
