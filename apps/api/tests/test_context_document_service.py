import asyncio

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.records import ContextDocumentRecord, KnowledgeChunkRecord
from app.services.context_document_service import ContextDocumentService


class FakeEmbeddings:
    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0] for _ in texts]

    async def aembed_query(self, query: str) -> list[float]:
        return [1.0]


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    return local_session()


def test_retrieve_respects_project_and_run_scope_and_filters_source_type() -> None:
    session = make_session()
    service = ContextDocumentService()
    session.add_all(
        [
            ContextDocumentRecord(
                project_id="project-1",
                run_id=None,
                source_type="knowledge",
                source_id="knowledge-1",
                path="docs/style-guide.md",
                content="project knowledge",
                excerpt="project knowledge",
                embedding=[1.0],
                document_metadata={"scope": "project"},
            ),
            ContextDocumentRecord(
                project_id="project-1",
                run_id="run-1",
                source_type="artifact",
                source_id="artifact-1",
                path="tasks/run-1/artifact.md",
                content="artifact from run one",
                excerpt="artifact from run one",
                embedding=[1.0],
                document_metadata={"scope": "run"},
            ),
            ContextDocumentRecord(
                project_id="project-1",
                run_id="run-2",
                source_type="artifact",
                source_id="artifact-2",
                path="tasks/run-2/artifact.md",
                content="artifact from run two",
                excerpt="artifact from run two",
                embedding=[1.0],
                document_metadata={"scope": "run"},
            ),
        ]
    )
    session.commit()

    items = asyncio.run(service.retrieve(session, "project-1", "query", FakeEmbeddings(), run_id="run-1"))

    assert {item["source_id"] for item in items} == {"knowledge-1", "artifact-1"}

    artifact_items = asyncio.run(
        service.retrieve(session, "project-1", "query", FakeEmbeddings(), run_id="run-1", source_types=["artifact"])
    )

    assert {item["source_id"] for item in artifact_items} == {"artifact-1"}


def test_bootstrap_backfills_legacy_knowledge_chunks() -> None:
    session = make_session()
    service = ContextDocumentService()
    session.add(
        KnowledgeChunkRecord(
            project_id="project-1",
            source="legacy/source.md",
            content="legacy knowledge chunk",
            embedding=[0.5],
            chunk_metadata={"tag": "legacy"},
        )
    )
    session.commit()

    created = service.bootstrap(session)
    documents = session.scalars(select(ContextDocumentRecord)).all()

    assert created == 1
    assert len(documents) == 1
    assert documents[0].source_type == "knowledge"
    assert documents[0].document_metadata["scope"] == "project"
    assert documents[0].document_metadata["legacy_chunk_id"]
