from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.approval import build_approval_context
from app.api.clarification import build_clarification_context, normalize_clarification_message
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
from app.models.records import ApprovalRecord, ClarificationRecord, CycleRecord, NodeExecutionRecord, ProjectRecord, RunRecord
from app.models.schemas import (
    ApprovalDecisionRequest,
    EventMessage,
    EventType,
    GraphResponse,
    KnowledgeIngestRequest,
    ClarificationRequest,
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
    PendingActionRead,
    ProjectTemplateProfileRead,
    QualityGateRead,
    Role,
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


@router.get("/runs/{run_id}/pending-action", response_model=PendingActionRead)
def get_run_pending_action(run_id: str, session: Session = Depends(get_session)) -> PendingActionRead:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    cycle = _get_active_cycle(session, run)
    checkpoint = container.checkpoint_store.latest_for_cycle(session, run_id=run.id, cycle_id=cycle.id)
    state = dict(checkpoint.serialized_state or {}) if checkpoint else {}
    latest_plan = container.context_document_service.get_current_shared_plan(session, run.id)
    action_type = "none"
    approval_context = None
    clarification_context = None
    if run.status == "WAITING_APPROVAL":
        action_type = "approval"
        approval_context = build_approval_context(latest_plan)
    elif run.status == "WAITING_CLARIFICATION":
        action_type = "clarification"
        clarification_context = build_clarification_context(state)
    elif run.status == "BLOCKED":
        action_type = "resume"
    return PendingActionRead(
        run_id=run.id,
        status=run.status,
        action_type=action_type,
        target_role=state.get("clarification_target_role"),
        reason=str(state.get("blocked_reason", "")),
        latest_plan_id=latest_plan.id if latest_plan else None,
        approval_state=state.get("approval_state"),
        approval_context=approval_context,
        clarification_context=clarification_context,
    )


@router.post("/runs/{run_id}/approve", response_model=RunRead)
async def approve_run(
    run_id: str,
    payload: ApprovalDecisionRequest,
    session: Session = Depends(get_session),
) -> RunRead:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    if run.status != "WAITING_APPROVAL":
        raise HTTPException(status_code=409, detail="Run is not waiting for approval.")
    cycle = _get_active_cycle(session, run)
    checkpoint = container.checkpoint_store.latest_for_cycle(session, run_id=run.id, cycle_id=cycle.id)
    if checkpoint is None:
        raise HTTPException(status_code=409, detail="Run has no checkpoint to approve.")
    latest_plan = container.context_document_service.get_current_shared_plan(session, run.id)
    if latest_plan is None:
        raise HTTPException(status_code=409, detail="Run has no shared plan to approve.")

    session.add(
        ApprovalRecord(
            run_id=run.id,
            cycle_id=cycle.id,
            shared_plan_id=latest_plan.id,
            approved=payload.approved,
            comment=payload.comment,
        )
    )
    state = dict(checkpoint.serialized_state or {})
    if payload.approved:
        latest_plan.approval_state = "approved"
        run.status = "RUNNING"
        cycle.status = "RUNNING"
        run.updated_at = cycle.updated_at
        state["approval_state"] = "approved"
        state["next_action"] = "continue"
        state["blocked_reason"] = None
        container.checkpoint_store.save(
            session,
            run_id=run.id,
            cycle_id=cycle.id,
            cycle_index=cycle.cycle_index,
            graph_kind=checkpoint.graph_kind,
            last_completed_role=state.get("last_completed_role"),
            serialized_state=state,
        )
        await container.event_bus.publish(
            session,
            run_id=run.id,
            event_type=EventType.APPROVAL_GRANTED,
            cycle_id=cycle.id,
            payload={"comment": payload.comment, "shared_plan_id": latest_plan.id},
        )
        session.commit()
        session.refresh(run)
        await container.runtime.start_run(run.id, resumed=True, force_restart=True)
        return to_run_read(run)

    latest_plan.approval_state = "rejected"
    run.status = "WAITING_CLARIFICATION"
    cycle.status = "WAITING_CLARIFICATION"
    state["approval_state"] = "rejected"
    state["next_action"] = "await_clarification"
    state["clarification_target_role"] = Role.CA.value
    state["blocked_reason"] = "approval_rejected"
    container.memory_service.add_memory(
        session,
        run_id=run.id,
        cycle_id=cycle.id,
        memory_type="approval_feedback",
        content=payload.comment or "Plan approval was rejected.",
        metadata={"target_role": Role.CA.value},
    )
    container.checkpoint_store.save(
        session,
        run_id=run.id,
        cycle_id=cycle.id,
        cycle_index=cycle.cycle_index,
        graph_kind=checkpoint.graph_kind,
        last_completed_role=state.get("last_completed_role"),
        serialized_state=state,
    )
    await container.event_bus.publish(
        session,
        run_id=run.id,
        event_type=EventType.APPROVAL_REJECTED,
        cycle_id=cycle.id,
        payload={"comment": payload.comment, "shared_plan_id": latest_plan.id},
    )
    session.commit()
    session.refresh(run)
    return to_run_read(run)


@router.post("/runs/{run_id}/clarify", response_model=RunRead)
async def clarify_run(
    run_id: str,
    payload: ClarificationRequest,
    session: Session = Depends(get_session),
) -> RunRead:
    container = get_container()
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    if run.status != "WAITING_CLARIFICATION":
        raise HTTPException(status_code=409, detail="Run is not waiting for clarification.")
    cycle = _get_active_cycle(session, run)
    checkpoint = container.checkpoint_store.latest_for_cycle(session, run_id=run.id, cycle_id=cycle.id)
    if checkpoint is None:
        raise HTTPException(status_code=409, detail="Run has no checkpoint to clarify.")
    try:
        normalized_message = normalize_clarification_message(payload.decision, payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    state = dict(checkpoint.serialized_state or {})
    target_role = str(state.get("clarification_target_role") or Role.PC.value)
    clarification = ClarificationRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        target_role=target_role,
        message=normalized_message,
        structured_context=payload.structured_context or {},
    )
    session.add(clarification)
    session.commit()
    session.refresh(clarification)
    container.memory_service.add_memory(
        session,
        run_id=run.id,
        cycle_id=cycle.id,
        memory_type="clarification",
        content=normalized_message,
        metadata={"target_role": target_role, "decision": payload.decision},
    )
    preferences = payload.structured_context.get("preferences") if isinstance(payload.structured_context, dict) else None
    container.memory_service.upsert_user_preferences(
        session,
        project_id=run.project_id,
        preferences=preferences,
        source="explicit",
    )
    clarification_history = list(state.get("clarification_history", []))
    clarification_history.append(
        {
            "id": clarification.id,
            "message": clarification.message,
            "structured_context": clarification.structured_context or {},
            "target_role": clarification.target_role,
            "decision": payload.decision,
        }
    )
    state["clarification_history"] = clarification_history
    state["next_action"] = "continue"
    state["blocked_reason"] = None
    state["clarification_target_role"] = None
    state["clarification_accepted_target_role"] = target_role if payload.decision == "accept_defaults" else None
    if payload.decision == "accept_defaults" and target_role == Role.PC.value:
        _sanitize_pc_outputs_after_accept_defaults(state)
        state["last_completed_role"] = Role.PC.value
        current = dict(state.get("retry_counts", {}))
        current[Role.PC.value] = 0
        state["retry_counts"] = current
        for node in session.scalars(select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id)).all():
            if node.role == Role.PC.value:
                node.retry_count = 0
                node.error_message = None
                continue
            if node.role not in {Role.CA.value, Role.FD.value, Role.BD.value, Role.QT.value, Role.DE.value}:
                continue
            node.status = "PENDING"
            node.retry_count = 0
            node.result_payload = None
            node.handoff_notes = None
            node.error_message = None
            node.context_snapshot = None
            node.started_at = None
            node.finished_at = None
        session.commit()
    else:
        state["approval_state"] = "pending"
        state["shared_plan_id"] = None
        state["active_plan_id"] = None
        _reset_nodes_for_clarification(session, cycle.id, target_role)
        if target_role == Role.PC.value:
            state["node_outputs"] = {}
            state["artifact_refs"] = {}
            state["retry_counts"] = {}
            state["last_completed_role"] = None
        else:
            for mapping_key, roles in {
                "node_outputs": [Role.CA.value, Role.FD.value, Role.BD.value, Role.QT.value, Role.DE.value],
                "artifact_refs": [Role.CA.value, Role.FD.value, Role.BD.value, Role.QT.value, Role.DE.value],
                "retry_counts": [Role.CA.value, Role.FD.value, Role.BD.value, Role.QT.value, Role.DE.value],
            }.items():
                current = dict(state.get(mapping_key, {}))
                for role_name in roles:
                    current.pop(role_name, None)
                state[mapping_key] = current
            state["last_completed_role"] = Role.PC.value if cycle.cycle_index == 1 else None
    run.status = "RUNNING"
    cycle.status = "RUNNING"
    container.checkpoint_store.save(
        session,
        run_id=run.id,
        cycle_id=cycle.id,
        cycle_index=cycle.cycle_index,
        graph_kind=checkpoint.graph_kind,
        last_completed_role=state.get("last_completed_role"),
        serialized_state=state,
    )
    await container.event_bus.publish(
        session,
        run_id=run.id,
        event_type=EventType.CLARIFICATION_RECEIVED,
        cycle_id=cycle.id,
        payload={"target_role": target_role, "message": normalized_message, "decision": payload.decision},
    )
    session.refresh(run)
    await container.runtime.start_run(run.id, resumed=True, force_restart=True)
    return to_run_read(run)


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


@router.get("/runs/{run_id}/quality-gate", response_model=QualityGateRead)
def get_run_quality_gate(run_id: str, session: Session = Depends(get_session)) -> QualityGateRead:
    run = session.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    cycles = session.scalars(
        select(CycleRecord)
        .where(CycleRecord.run_id == run.id)
        .order_by(CycleRecord.cycle_index.desc())
    ).all()
    cycle = None
    summary = None
    for candidate in cycles:
        candidate_summary = to_cycle_summary(session, candidate)
        if candidate_summary.quality_report is not None:
            cycle = candidate
            summary = candidate_summary
            break
    if cycle is None or summary is None:
        cycle = _get_active_cycle(session, run)
        summary = to_cycle_summary(session, cycle)
    return QualityGateRead(
        run_id=run.id,
        cycle_id=cycle.id,
        cycle_index=cycle.cycle_index,
        report=summary.quality_report,
    )


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
async def stream_run_events(run_id: str, after_sequence: int | None = None) -> StreamingResponse:
    container = get_container()
    with SessionLocal() as session:
        run = session.get(RunRecord, run_id)
        if run is None:
            raise HTTPException(status_code=404, detail="Run not found.")

    async def event_generator():
        with SessionLocal() as replay_session:
            replay_events = container.event_bus.replay(replay_session, run_id, after_sequence=after_sequence)
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


def _get_active_cycle(session: Session, run: RunRecord) -> CycleRecord:
    cycle = session.scalar(select(CycleRecord).where(CycleRecord.run_id == run.id, CycleRecord.cycle_index == run.current_cycle))
    if cycle is None:
        raise HTTPException(status_code=404, detail="Run has no active cycle.")
    return cycle


def _reset_nodes_for_clarification(session: Session, cycle_id: str, target_role: str) -> None:
    reset_roles = {Role.PC.value, Role.CA.value, Role.FD.value, Role.BD.value, Role.QT.value, Role.DE.value}
    if target_role == Role.CA.value:
        reset_roles = {Role.CA.value, Role.FD.value, Role.BD.value, Role.QT.value, Role.DE.value}
    nodes = session.scalars(select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle_id)).all()
    for node in nodes:
        if node.role not in reset_roles:
            continue
        node.status = "PENDING"
        node.retry_count = 0
        node.result_payload = None
        node.handoff_notes = None
        node.error_message = None
        node.context_snapshot = None
        node.started_at = None
        node.finished_at = None
    session.commit()


def _sanitize_pc_outputs_after_accept_defaults(state: dict) -> None:
    node_outputs = state.get("node_outputs")
    if not isinstance(node_outputs, dict):
        return
    pc_payload = node_outputs.get(Role.PC.value)
    if not isinstance(pc_payload, dict):
        return

    intent = pc_payload.get("intent")
    if isinstance(intent, dict):
        intent = dict(intent)
        intent["needs_clarification"] = False
        intent["clarifying_questions"] = []
        pc_payload["intent"] = intent

    fidelity = pc_payload.get("requirement_fidelity")
    if isinstance(fidelity, dict):
        fidelity = dict(fidelity)
        fidelity["clarification_needed"] = False
        fidelity["semantic_coverage_score"] = _score_floor(
            fidelity.get("semantic_coverage_score"),
            minimum=0.85,
        )
        fidelity["constraint_retention_score"] = _score_floor(
            fidelity.get("constraint_retention_score"),
            minimum=0.90,
        )
        pc_payload["requirement_fidelity"] = fidelity

    node_outputs[Role.PC.value] = pc_payload


def _score_floor(value: object, *, minimum: float) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = minimum
    if score > 1.0:
        score = score / 100.0
    return max(minimum, min(1.0, score))
