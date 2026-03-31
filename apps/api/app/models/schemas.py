from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Role(str, Enum):
    PC = "PC"
    CA = "CA"
    FD = "FD"
    BD = "BD"
    DE = "DE"
    QT = "QT"


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    FAILED_MAX_CYCLES = "FAILED_MAX_CYCLES"


class CycleStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class ProviderKind(str, Enum):
    CHAT = "CHAT"
    EMBEDDING = "EMBEDDING"


class EventType(str, Enum):
    RUN_CREATED = "run_created"
    CYCLE_STARTED = "cycle_started"
    NODE_STARTED = "node_started"
    NODE_LOG = "node_log"
    CONTEXT_INDEXED = "context_indexed"
    CONTEXT_ASSEMBLED = "context_assembled"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    CHECKPOINT_SAVED = "checkpoint_saved"
    CYCLE_REGENERATED = "cycle_regenerated"
    RUN_PAUSED = "run_paused"
    RUN_RESUMED = "run_resumed"
    RUN_COMPLETED = "run_completed"


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    template: str = "next-fastapi-template"


class ProjectRead(ProjectCreate):
    id: str
    created_at: datetime


class ProviderConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    kind: ProviderKind
    provider: str
    model: str
    base_url: str | None = None
    api_key: str | None = None
    is_default: bool = False
    settings: dict[str, Any] = Field(default_factory=dict)


class ProviderValidationRequest(BaseModel):
    config: ProviderConfig


class ProviderValidationResponse(BaseModel):
    ok: bool
    message: str


class ContextSourceType(str, Enum):
    KNOWLEDGE = "knowledge"
    ARTIFACT = "artifact"
    SHARED_PLAN = "shared_plan"
    MEMORY = "memory"
    REQUIREMENT = "requirement"


class KnowledgeIngestRequest(BaseModel):
    project_id: str
    source: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactManifest(BaseModel):
    id: str
    run_id: str
    cycle_id: str
    node_id: str
    artifact_type: str
    name: str
    path: str
    content_type: str
    summary: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class EventMessage(BaseModel):
    sequence: int
    type: EventType
    run_id: str
    cycle_id: str | None = None
    node_id: str | None = None
    timestamp: datetime
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkflowNodeView(BaseModel):
    id: str
    role: Role
    cycle_id: str
    cycle_index: int
    batch_index: int
    status: NodeStatus
    retry_count: int
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class WorkflowEdgeView(BaseModel):
    source: str
    target: str


class GraphResponse(BaseModel):
    run_id: str
    nodes: list[WorkflowNodeView]
    edges: list[WorkflowEdgeView]


class QualityDefectSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class QualityDefect(BaseModel):
    id: str = ""
    description: str = ""
    severity: QualityDefectSeverity = QualityDefectSeverity.MEDIUM
    location: str = ""
    suggestion: str = ""


class QualityReport(BaseModel):
    status: str
    defect_list: list[QualityDefect] = Field(default_factory=list)
    root_cause_guess: str = ""
    retest_scope: list[str] = Field(default_factory=list)
    remediation_requirement: str = ""


class RemediationRequirement(BaseModel):
    summary: str
    change_list: list[str] = Field(default_factory=list)


class CycleSummary(BaseModel):
    id: str
    run_id: str
    cycle_index: int
    status: CycleStatus
    remediation_requirement: str | None = None
    quality_report: QualityReport | None = None
    created_at: datetime
    updated_at: datetime
    nodes: list[WorkflowNodeView] = Field(default_factory=list)


class RunRequest(BaseModel):
    project_id: str
    requirement: str
    provider_name: str | None = None
    embedding_provider_name: str | None = None
    manual_approval: bool = False
    template_context: dict[str, Any] = Field(default_factory=dict)
    max_cycles: int | None = Field(default=None, ge=1, le=3)


class RunRead(BaseModel):
    id: str
    project_id: str
    requirement: str
    status: RunStatus
    current_cycle: int
    max_cycles: int
    provider_name: str
    embedding_provider_name: str
    manual_approval: bool
    task_root_path: str
    created_at: datetime
    updated_at: datetime


class RunDetail(RunRead):
    cycles: list[CycleSummary] = Field(default_factory=list)
    latest_artifacts: list[ArtifactManifest] = Field(default_factory=list)


class ContextSource(BaseModel):
    source_type: ContextSourceType
    source_id: str | None = None
    path: str | None = None
    excerpt: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    score: float | None = None
    scope: str | None = None
    section: str | None = None
    order_index: int | None = None
    included: bool = True


class AgentTaskContext(BaseModel):
    role: Role
    project_id: str
    run_id: str
    cycle_id: str
    cycle_index: int
    task_spec: dict[str, Any]
    shared_plan: dict[str, Any]
    shared_plan_id: str | None = None
    upstream_artifacts: list[ArtifactManifest] = Field(default_factory=list)
    retrieved_context: list[dict[str, Any]] = Field(default_factory=list)
    provider_config: ProviderConfig
    memories: list[str] = Field(default_factory=list)
    original_requirement: str
    template_context: dict[str, Any] = Field(default_factory=dict)
    template_context_origin: str = "explicit"
    context_sources: list[ContextSource] = Field(default_factory=list)
    context_metadata: dict[str, Any] = Field(default_factory=dict)


class SharedPlanVersionRead(BaseModel):
    id: str
    cycle_id: str
    version_index: int
    produced_by_role: str
    summary: str
    is_current: bool
    created_at: datetime


class SharedPlanRead(BaseModel):
    run_id: str
    latest_plan_id: str | None = None
    latest_plan: dict[str, Any] = Field(default_factory=dict)
    versions: list[SharedPlanVersionRead] = Field(default_factory=list)


class MemorySummaryRead(BaseModel):
    id: str
    run_id: str
    project_id: str | None = None
    cycle_id: str
    summary_type: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class NodeContextSourcesRead(BaseModel):
    run_id: str
    node_id: str
    context_sources: list[ContextSource] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectTemplateProfileRead(BaseModel):
    project_id: str
    latest: MemorySummaryRead | None = None
    versions: list[MemorySummaryRead] = Field(default_factory=list)


class AgentTaskResult(BaseModel):
    summary: str
    artifact_list: list[dict[str, Any]] = Field(default_factory=list)
    result_payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5
    handoff_notes: str = ""


class PCResultSchema(BaseModel):
    requirement_brief: str
    acceptance_criteria: dict[str, Any] = Field(default_factory=dict)
    work_breakdown: list[str] = Field(default_factory=list)
    summary: str = ""
    handoff_notes: str = ""
    confidence: float = 0.72


class CAResultSchema(BaseModel):
    shared_plan: dict[str, Any] = Field(default_factory=dict)
    interfaces: list[dict[str, Any]] = Field(default_factory=list)
    architecture_decisions: list[str] = Field(default_factory=list)
    summary: str = ""
    handoff_notes: str = ""
    confidence: float = 0.72


class ToolAgentSubmitPayload(BaseModel):
    summary: str
    handoff_notes: str = ""
    result_payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.72
