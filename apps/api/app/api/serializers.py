from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import CycleRecord, NodeExecutionRecord, ProjectRecord, RunRecord
from app.models.schemas import (
    ArtifactManifest,
    CycleStatus,
    CycleSummary,
    QualityReport,
    ProjectRead,
    RunDetail,
    RunRead,
    RunStatus,
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
    quality_report = _normalize_quality_report(cycle.quality_report) if cycle.quality_report else None
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
    return RunDetail(
        **to_run_read(run).model_dump(),
        cycles=[to_cycle_summary(session, cycle) for cycle in cycles],
        latest_artifacts=artifacts[:12],
    )


def _normalize_quality_report(raw_report: dict | None) -> QualityReport | None:
    if not raw_report:
        return None
    return QualityReport(
        status=str(raw_report.get("status", "FAIL")).upper(),
        defect_list=_normalize_string_list(raw_report.get("defect_list", [])),
        root_cause_guess=_stringify_value(raw_report.get("root_cause_guess", "")),
        retest_scope=_normalize_string_list(raw_report.get("retest_scope", [])),
        remediation_requirement=_stringify_value(raw_report.get("remediation_requirement", "")),
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
