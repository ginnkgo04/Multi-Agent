from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.serializers import (
    to_cycle_summary,
    to_memory_summary_read,
    to_node_context_sources_read,
    to_project_read,
    to_project_template_profile_read,
    to_run_detail,
    to_run_read,
    to_shared_plan_read,
)
from app.config import get_settings
from app.db import SessionLocal, get_session
from app.models.records import CycleRecord, ProjectRecord, RunRecord
from app.models.schemas import (
    EventMessage,
    EventType,
    GraphResponse,
    KnowledgeIngestRequest,
    ProjectCreate,
    ProjectRead,
    ProviderConfig,
    ProviderValidationRequest,
    ProviderValidationResponse,
    RunDetail,
    RunRead,
    RunRequest,
    CycleSummary,
    ArtifactManifest,
    MemorySummaryRead,
    NodeContextSourcesRead,
    ProjectTemplateProfileRead,
    SharedPlanRead,
)
from app.services.container import get_container

router = APIRouter()
settings = get_settings()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "pc_ca_chat_path": "native-provider-fallback-v1",
    }


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(session: Session = Depends(get_session)) -> list[ProjectRead]:
    records = session.scalars(select(ProjectRecord).order_by(ProjectRecord.created_at.desc())).all()
    return [to_project_read(record) for record in records]


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> ProjectRead:
    container = get_container()
    return container.requirement_intake.create_project(session, payload)


@router.get("/providers", response_model=list[ProviderConfig])
def list_providers(session: Session = Depends(get_session)) -> list[ProviderConfig]:
    container = get_container()
    return container.provider_registry.list_configs(session)


@router.post("/providers/validate", response_model=ProviderValidationResponse)
def validate_provider(payload: ProviderValidationRequest) -> ProviderValidationResponse:
    container = get_container()
    ok, message = container.provider_registry.validate(payload.config)
    return ProviderValidationResponse(ok=ok, message=message)


@router.post("/knowledge/ingest")
async def ingest_knowledge(payload: KnowledgeIngestRequest, session: Session = Depends(get_session)) -> dict[str, int]:
    container = get_container()
    _, embedding_provider = container.provider_registry.resolve_embedding_provider(session, settings.default_embedding_provider)
    chunks = await container.context_document_service.ingest_external_knowledge(session, payload, embedding_provider)
    return {"chunks": chunks}


@router.post("/runs", response_model=RunRead, status_code=status.HTTP_202_ACCEPTED)
async def create_run(payload: RunRequest, session: Session = Depends(get_session)) -> RunRead:
    container = get_container()
    project = session.get(ProjectRecord, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    provider_name = payload.provider_name or settings.default_chat_provider
    embedding_provider_name = payload.embedding_provider_name or settings.default_embedding_provider
    run = container.requirement_intake.create_run(session, payload, provider_name, embedding_provider_name)
    _, embedding_provider = container.provider_registry.resolve_embedding_provider(session, embedding_provider_name)
    indexed_chunks = await container.context_document_service.index_requirement(session, run=run, embedding_provider=embedding_provider)
    await container.event_bus.publish(
        session,
        run_id=run.id,
        event_type=EventType.RUN_CREATED,
        payload={
            "project_id": run.project_id,
            "requirement": run.requirement,
            "template_context_origin": run.template_context_origin,
            "indexed_requirement_chunks": indexed_chunks,
        },
    )
    await container.event_bus.publish(
        session,
        run_id=run.id,
        event_type=EventType.CONTEXT_INDEXED,
        payload={
            "source_type": "requirement",
            "chunk_count": indexed_chunks,
            "template_context_origin": run.template_context_origin,
        },
    )
    await container.runtime.start_run(run.id)
    return to_run_read(run)


@router.get("/runs", response_model=list[RunRead])
def list_runs(session: Session = Depends(get_session)) -> list[RunRead]:
    records = session.scalars(select(RunRecord).order_by(RunRecord.created_at.desc())).all()
    return [to_run_read(record) for record in records]


@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str, session: Session = Depends(get_session)) -> RunDetail:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    artifacts = container.artifact_store.list_run_artifacts(session, run_id)
    return to_run_detail(session, run, artifacts)


@router.get("/runs/{run_id}/graph", response_model=GraphResponse)
def get_run_graph(run_id: str, session: Session = Depends(get_session)) -> GraphResponse:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return container.graph_builder.graph_view(session, run_id)


@router.get("/runs/{run_id}/artifacts", response_model=list[ArtifactManifest])
def get_run_artifacts(run_id: str, session: Session = Depends(get_session)) -> list[ArtifactManifest]:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return container.artifact_store.list_run_artifacts(session, run_id)


@router.get("/runs/{run_id}/cycles", response_model=list[CycleSummary])
def get_run_cycles(run_id: str, session: Session = Depends(get_session)) -> list[CycleSummary]:
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    cycles = session.scalars(select(CycleRecord).where(CycleRecord.run_id == run_id).order_by(CycleRecord.cycle_index)).all()
    return [to_cycle_summary(session, cycle) for cycle in cycles]


@router.get("/runs/{run_id}/shared-plan", response_model=SharedPlanRead)
def get_run_shared_plan(run_id: str, session: Session = Depends(get_session)) -> SharedPlanRead:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    records = container.context_document_service.list_shared_plans(session, run_id)
    return to_shared_plan_read(run_id, records)


@router.get("/runs/{run_id}/nodes/{node_id}/context-sources", response_model=NodeContextSourcesRead)
def get_node_context_sources(run_id: str, node_id: str, session: Session = Depends(get_session)) -> NodeContextSourcesRead:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    snapshot = container.context_document_service.get_node_context_snapshot(session, run_id=run_id, node_id=node_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Node not found.")
    return to_node_context_sources_read(run_id, node_id, snapshot)


@router.get("/runs/{run_id}/memory-summaries", response_model=list[MemorySummaryRead])
def get_run_memory_summaries(run_id: str, session: Session = Depends(get_session)) -> list[MemorySummaryRead]:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    records = container.memory_service.list_summaries(session, run_id)
    return [to_memory_summary_read(record) for record in records]


@router.get("/projects/{project_id}/template-profile", response_model=ProjectTemplateProfileRead)
def get_project_template_profile(project_id: str, session: Session = Depends(get_session)) -> ProjectTemplateProfileRead:
    container = get_container()
    project = session.get(ProjectRecord, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    records = container.memory_service.list_project_template_profiles(session, project_id)
    return to_project_template_profile_read(project_id, records)


@router.post("/runs/{run_id}/resume", response_model=RunRead)
async def resume_run(run_id: str, session: Session = Depends(get_session)) -> RunRead:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    try:
        container.retry_manager.prepare_resume(session, run)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    await container.event_bus.publish(
        session,
        run_id=run.id,
        event_type=EventType.RUN_RESUMED,
        payload={"current_cycle": run.current_cycle},
    )
    await container.runtime.start_run(run.id, resumed=True, force_restart=True)
    session.refresh(run)
    return to_run_read(run)


@router.get("/runs/{run_id}/events/stream")
async def stream_run_events(run_id: str) -> StreamingResponse:
    container = get_container()
    with SessionLocal() as session:
        run = session.get(RunRecord, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found.")

    async def event_generator():
        with SessionLocal() as replay_session:
            replay_events = container.event_bus.replay(replay_session, run_id)
        for event in replay_events:
            yield _format_sse(event)
        queue = await container.event_bus.subscribe(run_id)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    yield _format_sse(event)
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"
        finally:
            await container.event_bus.unsubscribe(run_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _format_sse(message: EventMessage) -> str:
    return f"data: {json.dumps(message.model_dump(mode='json'), ensure_ascii=False)}\n\n"
