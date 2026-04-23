from __future__ import annotations

import json
import math
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import ContextDocumentRecord, KnowledgeChunkRecord, SharedPlanRecord
from app.models.schemas import ContextSourceType, KnowledgeIngestRequest


class ContextDocumentService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def ingest_external_knowledge(self, session: Session, payload: KnowledgeIngestRequest, embedding_provider) -> int:
        metadata = {
            **(payload.metadata or {}),
            "scope": "project",
        }
        return await self._index_text(
            session,
            project_id=payload.project_id,
            run_id=None,
            cycle_id=None,
            node_id=None,
            source_type=ContextSourceType.KNOWLEDGE.value,
            source_id=None,
            path=payload.source,
            content=payload.content,
            metadata=metadata,
            embedding_provider=embedding_provider,
        )

    async def index_requirement(self, session: Session, *, run, embedding_provider) -> int:
        return await self._index_text(
            session,
            project_id=run.project_id,
            run_id=run.id,
            cycle_id=None,
            node_id=None,
            source_type=ContextSourceType.REQUIREMENT.value,
            source_id=run.id,
            path=f"runs/{run.id}/requirement",
            content=run.requirement,
            metadata={"scope": "run"},
            embedding_provider=embedding_provider,
        )

    async def index_artifacts(
        self,
        session: Session,
        *,
        project_id: str,
        artifacts: list,
        embedding_provider,
    ) -> int:
        total = 0
        for artifact in artifacts:
            preview = str((artifact.metadata or {}).get("content_preview", ""))
            body = preview or artifact.summary or artifact.name
            total += await self._index_text(
                session,
                project_id=project_id,
                run_id=artifact.run_id,
                cycle_id=artifact.cycle_id,
                node_id=artifact.node_id,
                source_type=ContextSourceType.ARTIFACT.value,
                source_id=artifact.id,
                path=artifact.path,
                content=body,
                metadata={
                    **(artifact.metadata or {}),
                    "scope": "run",
                    "artifact_type": artifact.artifact_type,
                },
                embedding_provider=embedding_provider,
            )
        return total

    async def index_shared_plan(self, session: Session, *, project_id: str, record: SharedPlanRecord, embedding_provider) -> int:
        return await self._index_text(
            session,
            project_id=project_id,
            run_id=record.run_id,
            cycle_id=record.cycle_id,
            node_id=None,
            source_type=ContextSourceType.SHARED_PLAN.value,
            source_id=record.id,
            path=f"runs/{record.run_id}/shared-plans/{record.id}",
            content=self._shared_plan_text(record),
            metadata={
                "scope": "run",
                "version_index": record.version_index,
                "produced_by_role": record.produced_by_role,
                "is_current": record.is_current,
                "plan_kind": record.plan_kind,
                "approval_state": record.approval_state,
            },
            embedding_provider=embedding_provider,
        )

    async def index_memory_summary(
        self,
        session: Session,
        *,
        record,
        embedding_provider,
    ) -> int:
        scope = "project" if record.summary_type == "project_template_profile" else "run"
        return await self._index_text(
            session,
            project_id=record.project_id or self._project_id_for_run(session, record.run_id),
            run_id=record.run_id,
            cycle_id=record.cycle_id,
            node_id=None,
            source_type=ContextSourceType.MEMORY.value,
            source_id=record.id,
            path=f"runs/{record.run_id}/memory-summaries/{record.id}",
            content=record.content,
            metadata={
                **(record.summary_metadata or {}),
                "scope": scope,
                "summary_type": record.summary_type,
            },
            embedding_provider=embedding_provider,
        )

    async def retrieve(
        self,
        session: Session,
        project_id: str,
        query: str,
        embedding_provider,
        *,
        run_id: str | None = None,
        top_k: int | None = None,
        source_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        records = session.scalars(select(ContextDocumentRecord).where(ContextDocumentRecord.project_id == project_id)).all()
        candidates: list[ContextDocumentRecord] = []
        for record in records:
            metadata = record.document_metadata or {}
            scope = metadata.get("scope", "run")
            if scope == "project":
                candidates.append(record)
                continue
            if run_id and record.run_id == run_id:
                candidates.append(record)
        if source_types:
            allowed = set(source_types)
            candidates = [record for record in candidates if record.source_type in allowed]
        if not candidates:
            return []
        query_vector = await self._embed_query(embedding_provider, query)
        scored: list[tuple[float, ContextDocumentRecord]] = []
        for record in candidates:
            scored.append((self._cosine_similarity(query_vector, record.embedding or []), record))
        scored.sort(key=lambda item: item[0], reverse=True)
        top_records = scored[: (top_k or self.settings.retriever_top_k)]
        items = []
        for score, record in top_records:
            if score <= 0:
                continue
            metadata = record.document_metadata or {}
            items.append(
                {
                    "source_type": record.source_type,
                    "source_id": record.source_id,
                    "path": record.path,
                    "score": round(score, 4),
                    "excerpt": record.excerpt,
                    "metadata": metadata,
                    "scope": metadata.get("scope"),
                    "source": record.path or record.source_type,
                    "content": record.content,
                }
            )
        return items

    def create_shared_plan(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str,
        produced_by_role: str,
        plan_payload: dict[str, Any],
        summary: str,
        plan_kind: str = "initial",
        approval_state: str = "pending",
        parent_plan_id: str | None = None,
    ) -> SharedPlanRecord:
        all_records = session.scalars(select(SharedPlanRecord).where(SharedPlanRecord.run_id == run_id)).all()
        current_records = [
            record
            for record in all_records
            if record.is_current
        ]
        version_index = max((record.version_index for record in all_records), default=0) + 1
        for record in current_records:
            record.is_current = False
        record = SharedPlanRecord(
            run_id=run_id,
            cycle_id=cycle_id,
            version_index=version_index,
            produced_by_role=produced_by_role,
            plan_kind=plan_kind,
            approval_state=approval_state,
            parent_plan_id=parent_plan_id,
            plan_payload=plan_payload,
            summary=summary,
            is_current=True,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def get_current_shared_plan(self, session: Session, run_id: str) -> SharedPlanRecord | None:
        current = session.scalar(
            select(SharedPlanRecord).where(SharedPlanRecord.run_id == run_id, SharedPlanRecord.is_current == True)  # noqa: E712
            .order_by(desc(SharedPlanRecord.created_at))
        )
        if current is not None:
            return current
        return session.scalar(select(SharedPlanRecord).where(SharedPlanRecord.run_id == run_id).order_by(desc(SharedPlanRecord.created_at)))

    def list_shared_plans(self, session: Session, run_id: str) -> list[SharedPlanRecord]:
        return list(session.scalars(select(SharedPlanRecord).where(SharedPlanRecord.run_id == run_id).order_by(SharedPlanRecord.created_at)).all())

    def get_node_context_snapshot(self, session: Session, *, run_id: str, node_id: str) -> dict[str, Any] | None:
        from app.models.records import NodeExecutionRecord

        node = session.scalar(select(NodeExecutionRecord).where(NodeExecutionRecord.id == node_id, NodeExecutionRecord.run_id == run_id))
        if node is None:
            return None
        return node.context_snapshot or {"context_sources": [], "metadata": {}}

    def bootstrap(self, session: Session) -> int:
        count = 0
        for chunk in session.scalars(select(KnowledgeChunkRecord)).all():
            existing = session.scalar(
                select(ContextDocumentRecord).where(
                    ContextDocumentRecord.source_type == ContextSourceType.KNOWLEDGE.value,
                    ContextDocumentRecord.source_id == chunk.id,
                )
            )
            if existing is not None:
                continue
            session.add(
                ContextDocumentRecord(
                    project_id=chunk.project_id,
                    run_id=None,
                    cycle_id=None,
                    node_id=None,
                    source_type=ContextSourceType.KNOWLEDGE.value,
                    source_id=chunk.id,
                    path=chunk.source,
                    content=chunk.content,
                    excerpt=self._excerpt(chunk.content),
                    embedding=chunk.embedding or [],
                    document_metadata={
                        **(chunk.chunk_metadata or {}),
                        "scope": "project",
                        "legacy_chunk_id": chunk.id,
                    },
                )
            )
            count += 1
        if count:
            session.commit()
        return count

    async def _index_text(
        self,
        session: Session,
        *,
        project_id: str,
        run_id: str | None,
        cycle_id: str | None,
        node_id: str | None,
        source_type: str,
        source_id: str | None,
        path: str | None,
        content: str,
        metadata: dict[str, Any],
        embedding_provider,
    ) -> int:
        chunks = self._chunk_text(content)
        embeddings = await self._embed_many(embedding_provider, chunks) if embedding_provider is not None else [[] for _ in chunks]
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            session.add(
                ContextDocumentRecord(
                    project_id=project_id,
                    run_id=run_id,
                    cycle_id=cycle_id,
                    node_id=node_id,
                    source_type=source_type,
                    source_id=source_id,
                    path=path,
                    content=chunk,
                    excerpt=self._excerpt(chunk),
                    embedding=embedding,
                    document_metadata=metadata,
                )
            )
        session.commit()
        return len(chunks)

    @staticmethod
    def _shared_plan_text(record: SharedPlanRecord) -> str:
        payload = record.plan_payload or {}
        summary = record.summary or ""
        return (
            f"Plan kind: {record.plan_kind}\n"
            f"Approval state: {record.approval_state}\n"
            f"{summary}\n{json.dumps(payload, ensure_ascii=False)}"
        )

    @staticmethod
    def _project_id_for_run(session: Session, run_id: str) -> str:
        from app.models.records import RunRecord

        run = session.get(RunRecord, run_id)
        if run is None:
            raise ValueError(f"Run '{run_id}' was not found while resolving project context.")
        return run.project_id

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
    def _excerpt(content: str, limit: int = 240) -> str:
        return " ".join(content.split())[:limit]

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
