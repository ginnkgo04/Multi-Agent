from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.agents.base import WorkflowAgent
from app.config import get_settings
from app.models.records import CycleRecord, EventRecord, MemorySummaryRecord, NodeExecutionRecord, ProjectRecord, RunRecord, SharedPlanRecord
from app.models.schemas import (
    ArtifactManifest,
    CycleStatus,
    CycleSummary,
    MemorySummaryRead,
    NodeContextSourcesRead,
    QualityDefect,
    QualityReport,
    ProjectTemplateProfileRead,
    ProjectRead,
    RunDetail,
    RunRead,
    RunStatus,
    SharedPlanRead,
    SharedPlanVersionRead,
    WorkflowNodeView,
    NodeStatus,
    Role,
)

settings = get_settings()


def to_project_read(record: ProjectRecord) -> ProjectRead:
    return ProjectRead.model_validate(record, from_attributes=True)


def to_run_read(record: RunRecord) -> RunRead:
    return RunRead(
        id=record.id,
        project_id=record.project_id,
        requirement=record.requirement,
        status=RunStatus(record.status),
        current_cycle=record.current_cycle,
        max_cycles=record.max_cycles,
        provider_name=record.provider_name,
        embedding_provider_name=record.embedding_provider_name,
        manual_approval=record.manual_approval,
        task_root_path=str(settings.task_root_dir / record.id),
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def to_cycle_summary(session: Session, cycle: CycleRecord) -> CycleSummary:
    nodes = session.scalars(
        select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id).order_by(NodeExecutionRecord.batch_index)
    ).all()
    qt_completed = any(node.role == Role.QT.value and node.status == NodeStatus.COMPLETED.value for node in nodes)
    quality_report = _normalize_quality_report(cycle.quality_report) if cycle.quality_report and qt_completed else None
    return CycleSummary(
        id=cycle.id,
        run_id=cycle.run_id,
        cycle_index=cycle.cycle_index,
        status=CycleStatus(cycle.status),
        remediation_requirement=cycle.remediation_requirement,
        quality_report=quality_report,
        created_at=cycle.created_at,
        updated_at=cycle.updated_at,
        nodes=[
            WorkflowNodeView(
                id=node.id,
                role=Role(node.role),
                cycle_id=node.cycle_id,
                cycle_index=cycle.cycle_index,
                batch_index=node.batch_index,
                status=NodeStatus(node.status),
                retry_count=node.retry_count,
                error_message=node.error_message,
                started_at=node.started_at,
                finished_at=node.finished_at,
            )
            for node in nodes
        ],
    )


def to_run_detail(session: Session, run: RunRecord, artifacts: list[ArtifactManifest]) -> RunDetail:
    cycles = session.scalars(select(CycleRecord).where(CycleRecord.run_id == run.id).order_by(CycleRecord.cycle_index)).all()
    latest_event_sequence = session.scalar(select(func.max(EventRecord.sequence)).where(EventRecord.run_id == run.id)) or 0
    return RunDetail(
        **to_run_read(run).model_dump(),
        latest_event_sequence=latest_event_sequence,
        cycles=[to_cycle_summary(session, cycle) for cycle in cycles],
        latest_artifacts=artifacts[:12],
    )


def to_shared_plan_read(run_id: str, records: list[SharedPlanRecord]) -> SharedPlanRead:
    latest = next((record for record in reversed(records) if record.is_current), records[-1] if records else None)
    return SharedPlanRead(
        run_id=run_id,
        latest_plan_id=latest.id if latest else None,
        latest_plan=dict(latest.plan_payload or {}) if latest else {},
        latest_approval_state=latest.approval_state if latest else None,
        versions=[
            SharedPlanVersionRead(
                id=record.id,
                cycle_id=record.cycle_id,
                version_index=record.version_index,
                produced_by_role=record.produced_by_role,
                summary=record.summary,
                is_current=record.is_current,
                plan_kind=record.plan_kind,
                approval_state=record.approval_state,
                parent_plan_id=record.parent_plan_id,
                created_at=record.created_at,
            )
            for record in records
        ],
    )


def to_memory_summary_read(record: MemorySummaryRecord) -> MemorySummaryRead:
    return MemorySummaryRead(
        id=record.id,
        run_id=record.run_id,
        project_id=record.project_id,
        cycle_id=record.cycle_id,
        summary_type=record.summary_type,
        content=record.content,
        metadata=record.summary_metadata or {},
        created_at=record.created_at,
    )


def to_node_context_sources_read(run_id: str, node_id: str, snapshot: dict) -> NodeContextSourcesRead:
    return NodeContextSourcesRead(
        run_id=run_id,
        node_id=node_id,
        context_sources=snapshot.get("context_sources", []),
        metadata=snapshot.get("metadata", {}),
    )


def to_project_template_profile_read(project_id: str, records: list[MemorySummaryRecord]) -> ProjectTemplateProfileRead:
    latest = next((record for record in records if (record.summary_metadata or {}).get("is_current")), records[0] if records else None)
    return ProjectTemplateProfileRead(
        project_id=project_id,
        latest=to_memory_summary_read(latest) if latest else None,
        versions=[to_memory_summary_read(record) for record in records],
    )


def _normalize_quality_report(raw_report: dict | None) -> QualityReport | None:
    if not raw_report:
        return None
    defects = [
        QualityDefect.model_validate(defect)
        for defect in WorkflowAgent._normalize_quality_defect_list(raw_report.get("defect_list", []))
    ]
    return QualityReport(
        status=WorkflowAgent._normalize_quality_status(raw_report.get("status", "FAIL"), [defect.model_dump(mode="json") for defect in defects]),
        defect_list=defects,
        root_cause_guess=_stringify_value(raw_report.get("root_cause_guess", "")),
        retest_scope=_normalize_string_list(raw_report.get("retest_scope", [])),
        remediation_requirement=_stringify_value(raw_report.get("remediation_requirement", "")),
        approval_recommended=bool(raw_report.get("approval_recommended", False)),
    )


def _normalize_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            text = _stringify_value(item).strip()
            if text:
                items.append(text)
        return items
    text = _stringify_value(value).strip()
    return [text] if text else []


def _stringify_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        preferred_keys = ("description", "summary", "message", "title", "id", "severity", "location", "suggestion")
        parts = []
        for key in preferred_keys:
            item = value.get(key)
            if item:
                parts.append(f"{key}: {item}")
        if parts:
            return " | ".join(parts)
        return str(value)
    if isinstance(value, list):
        return "; ".join(_stringify_value(item) for item in value if _stringify_value(item).strip())
    return str(value)
