import asyncio
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.records import ArtifactRecord, ContextDocumentRecord, CycleRecord, MemoryRecord, MemorySummaryRecord, NodeExecutionRecord, ProjectRecord, RunRecord, SharedPlanRecord
from app.models.schemas import ProviderConfig, ProviderKind, Role, RunRequest
from app.services.artifact_store import ArtifactStore
from app.services.context_assembler import ContextAssembler
from app.services.context_budgeter import ContextBudgeter
from app.services.context_document_service import ContextDocumentService
from app.services.memory_service import MemoryService
from app.services.requirement_intake import RequirementIntakeService


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


def test_requirement_intake_inherits_project_template_profile_when_request_is_empty(tmp_path: Path) -> None:
    session = make_session()
    memory_service = MemoryService()
    intake = RequirementIntakeService(memory_service)
    intake.settings.task_root_dir = tmp_path

    project = ProjectRecord(name="Demo", template="next-fastapi-template")
    session.add(project)
    session.commit()
    session.refresh(project)
    memory_service.create_summary(
        session,
        run_id="seed-run",
        project_id=project.id,
        cycle_id="seed-cycle",
        summary_type="project_template_profile",
        content="seed profile",
        metadata={
            "is_current": True,
            "template_context": {"design": "consistent", "stack": "next-fastapi"},
        },
    )

    run = intake.create_run(
        session,
        payload=RunRequest(
            project_id=project.id,
            requirement="Ship a landing page",
            template_context={},
            manual_approval=False,
            max_cycles=1,
        ),
        provider_name="chat",
        embedding_provider_name="embed",
    )

    assert run.template_context == {"design": "consistent", "stack": "next-fastapi"}
    assert run.template_context_origin == "project_profile"


def test_context_assembler_uses_current_shared_plan_and_orders_context_sources(tmp_path: Path) -> None:
    session = make_session()
    project = ProjectRecord(name="Demo", template="next-fastapi-template")
    session.add(project)
    session.commit()
    session.refresh(project)
    run = RunRecord(
        project_id=project.id,
        requirement="Build a dashboard",
        status="RUNNING",
        provider_name="chat",
        embedding_provider_name="embed",
        template_context={"stack": "next-fastapi"},
        template_context_origin="explicit",
    )
    session.add(run)
    session.flush()
    cycle = CycleRecord(run_id=run.id, cycle_index=1, status="RUNNING")
    session.add(cycle)
    session.flush()
    ca_node = NodeExecutionRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        role=Role.CA.value,
        batch_index=1,
        status="COMPLETED",
        result_payload={"shared_plan": {"version": "old-payload"}},
    )
    fd_node = NodeExecutionRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        role=Role.FD.value,
        batch_index=2,
        status="PENDING",
        task_spec={"focus": "frontend"},
    )
    session.add_all([ca_node, fd_node])
    session.flush()
    artifact = ArtifactRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        node_id=ca_node.id,
        artifact_type="report",
        name="architecture/solution.md",
        path=str(tmp_path / "architecture" / "solution.md"),
        summary="Architecture summary",
        artifact_metadata={"content_preview": "architecture preview"},
    )
    shared_plan = SharedPlanRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        version_index=2,
        produced_by_role=Role.CA.value,
        plan_payload={"version": "current-record"},
        summary="Current shared plan",
        is_current=True,
    )
    project_profile = MemorySummaryRecord(
        run_id=run.id,
        project_id=project.id,
        cycle_id=cycle.id,
        summary_type="project_template_profile",
        content="Project template profile",
        summary_metadata={"is_current": True, "template_context": {"stack": "next-fastapi"}},
    )
    cycle_summary = MemorySummaryRecord(
        run_id=run.id,
        project_id=project.id,
        cycle_id=cycle.id,
        summary_type="cycle_summary",
        content="Cycle summary",
        summary_metadata={"status": "PASS"},
    )
    memory = MemoryRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        memory_type="fd_summary",
        content="Recent memory",
        memory_metadata={"role": "FD"},
    )
    knowledge_doc = ContextDocumentRecord(
        project_id=project.id,
        run_id=None,
        source_type="knowledge",
        source_id="knowledge-1",
        path="docs/reference.md",
        content="Reference knowledge",
        excerpt="Reference knowledge",
        embedding=[1.0],
        document_metadata={"scope": "project"},
    )
    session.add_all([artifact, shared_plan, project_profile, cycle_summary, memory, knowledge_doc])
    session.commit()

    assembler = ContextAssembler(
        ArtifactStore(),
        MemoryService(),
        ContextDocumentService(),
        ContextBudgeter(4000),
    )
    provider = ProviderConfig(id="embed", name="embed", kind=ProviderKind.EMBEDDING, provider="openai-compatible", model="fake")

    context = asyncio.run(
        assembler.build_context(
            session,
            run=run,
            cycle=cycle,
            node=fd_node,
            chat_config=provider,
            embedding_provider=FakeEmbeddings(),
        )
    )

    assert context.shared_plan == {"version": "current-record"}
    assert context.shared_plan_id == shared_plan.id
    assert [source.section for source in context.context_sources] == [
        "requirement",
        "shared_plan",
        "project_template_profile",
        "upstream_artifacts",
        "retrieved_docs",
        "cycle_summaries",
        "recent_memories",
    ]


def test_context_budgeter_trims_low_priority_context_first() -> None:
    budgeter = ContextBudgeter(char_budget=120)
    sources = [
        {"section": "requirement", "excerpt": "r" * 30, "metadata": {}, "included": True},
        {"section": "shared_plan", "excerpt": "s" * 30, "metadata": {}, "included": True},
        {"section": "recent_memories", "excerpt": "m" * 20, "metadata": {}, "included": True},
        {"section": "retrieved_docs", "excerpt": "l" * 10, "metadata": {}, "included": True, "score": 0.1},
        {"section": "retrieved_docs", "excerpt": "h" * 10, "metadata": {}, "included": True, "score": 0.9},
        {"section": "upstream_artifacts", "excerpt": "a" * 60, "metadata": {}, "included": True},
    ]

    budgeted, metadata = budgeter.apply(sources)

    assert budgeted[0]["included"] is True
    assert budgeted[1]["included"] is True
    assert budgeted[2]["included"] is False
    assert budgeted[3]["included"] is False
    assert metadata["final_chars"] <= metadata["char_budget"]
    assert len(budgeted[5]["excerpt"]) < 60
