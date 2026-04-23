from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic import model_validator


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
    WAITING_APPROVAL = "WAITING_APPROVAL"
    WAITING_CLARIFICATION = "WAITING_CLARIFICATION"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    FAILED_MAX_CYCLES = "FAILED_MAX_CYCLES"


class CycleStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    WAITING_CLARIFICATION = "WAITING_CLARIFICATION"
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
    PLAN_DRAFTED = "plan_drafted"
    APPROVAL_REQUIRED = "approval_required"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    CLARIFICATION_REQUIRED = "clarification_required"
    CLARIFICATION_RECEIVED = "clarification_received"
    QUALITY_GATE_PASSED = "quality_gate_passed"
    QUALITY_GATE_FAILED = "quality_gate_failed"
    DELIVERY_COMPLETED = "delivery_completed"


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
    CLARIFICATION = "clarification"
    PREFERENCE = "preference"


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
    owner_role: str = ""
    location: str = ""
    suggestion: str = ""
    expected_behavior: str = ""
    actual_behavior: str = ""
    fix_guidance: str = ""
    requires_plan_update: bool = False


class QualityReport(BaseModel):
    status: str
    defect_list: list[QualityDefect] = Field(default_factory=list)
    root_cause_guess: str = ""
    retest_scope: list[str] = Field(default_factory=list)
    remediation_requirement: str = ""
    approval_recommended: bool = False


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
    latest_event_sequence: int = 0
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


class WorkspaceFileSnapshot(BaseModel):
    path: str
    content: str = ""
    exists: bool = True
    size_bytes: int = 0


class EditOperation(BaseModel):
    path: str
    operation: Literal["create", "update", "delete"]
    strategy: Literal["create", "replace", "insert_before", "insert_after", "patch", "delete"]
    summary: str = ""
    content: str = ""
    old_text: str = ""
    new_text: str = ""
    anchors: list[str] = Field(default_factory=list)
    unified_diff: str = ""

    @model_validator(mode="after")
    def validate_operation_strategy(self) -> "EditOperation":
        if self.operation == "create":
            if self.strategy != "create":
                raise ValueError("create operations require strategy='create'")
            if not self.content:
                raise ValueError("create operations require non-empty content")
            return self

        if self.operation == "delete":
            if self.strategy != "delete":
                raise ValueError("delete operations require strategy='delete'")
            return self

        allowed_update_strategies = {"replace", "insert_before", "insert_after", "patch"}
        if self.strategy not in allowed_update_strategies:
            raise ValueError("update operations require a valid update strategy")

        if self.strategy == "replace" and (not self.old_text or not self.new_text):
            raise ValueError("replace updates require both old_text and new_text")

        if self.strategy == "patch" and not self.unified_diff:
            raise ValueError("patch updates require unified_diff")

        if self.strategy in {"insert_before", "insert_after"} and (
            not self.anchors or not self.new_text
        ):
            raise ValueError("insert updates require at least one anchor and non-empty new_text")

        return self


class EditPlan(BaseModel):
    operations: list[EditOperation] = Field(default_factory=list)


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
    active_plan_id: str | None = None
    plan_kind: str = "initial"
    approval_state: str = "not_required"
    clarification_history: list[dict[str, Any]] = Field(default_factory=list)
    requirement_baseline: str = ""
    preference_profile: dict[str, Any] = Field(default_factory=dict)
    allowed_write_roots: list[str] = Field(default_factory=list)
    workspace_manifest: list[str] = Field(default_factory=list)
    workspace_snapshots: list[WorkspaceFileSnapshot] = Field(default_factory=list)


class SharedPlanVersionRead(BaseModel):
    id: str
    cycle_id: str
    version_index: int
    produced_by_role: str
    summary: str
    is_current: bool
    plan_kind: str = "initial"
    approval_state: str = "pending"
    parent_plan_id: str | None = None
    created_at: datetime


class SharedPlanRead(BaseModel):
    run_id: str
    latest_plan_id: str | None = None
    latest_plan: dict[str, Any] = Field(default_factory=dict)
    latest_approval_state: str | None = None
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


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    comment: str = ""


class ClarificationContextRead(BaseModel):
    requirement_brief: str = ""
    clarifying_questions: list[str] = Field(default_factory=list)
    assumed_defaults: list[str] = Field(default_factory=list)
    acceptance_criteria: dict[str, Any] = Field(default_factory=dict)
    work_breakdown: list[str] = Field(default_factory=list)
    clarification_history: list[dict[str, Any]] = Field(default_factory=list)


class ClarificationRequest(BaseModel):
    decision: Literal["accept_defaults", "reject_defaults"]
    message: str = ""
    structured_context: dict[str, Any] = Field(default_factory=dict)


class ApprovalContextRead(BaseModel):
    summary: str = ""
    plan_kind: str = "initial"
    approval_state: str = "pending"
    execution_contract: dict[str, Any] = Field(default_factory=dict)
    interfaces: list[dict[str, Any]] = Field(default_factory=list)
    architecture_decisions: list[str] = Field(default_factory=list)
    remediation_plan: dict[str, Any] = Field(default_factory=dict)


class PendingActionRead(BaseModel):
    run_id: str
    status: RunStatus
    action_type: str
    target_role: str | None = None
    reason: str = ""
    latest_plan_id: str | None = None
    approval_state: str | None = None
    approval_context: ApprovalContextRead | None = None
    clarification_context: ClarificationContextRead | None = None


class QualityGateRead(BaseModel):
    run_id: str
    cycle_id: str
    cycle_index: int
    report: QualityReport | None = None


class AgentTaskResult(BaseModel):
    summary: str
    artifact_list: list[dict[str, Any]] = Field(default_factory=list)
    result_payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5
    handoff_notes: str = ""
    edit_operations: list[EditOperation] = Field(default_factory=list)


class IntentLayerSchema(BaseModel):
    scope: str = ""
    app_type: str = ""
    confidence: float = 0.0
    needs_clarification: bool = False
    clarifying_questions: list[str] = Field(default_factory=list)
    key_entities: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class RequirementFidelitySchema(BaseModel):
    semantic_coverage_score: float = 0.0
    constraint_retention_score: float = 0.0
    unmapped_items: list[str] = Field(default_factory=list)
    assumed_defaults: list[str] = Field(default_factory=list)
    clarification_needed: bool = False


class PCResultSchema(BaseModel):
    intent: IntentLayerSchema = Field(default_factory=IntentLayerSchema)
    requirement_brief: str
    acceptance_criteria: dict[str, Any] = Field(default_factory=dict)
    work_breakdown: list[str] = Field(default_factory=list)
    requirement_fidelity: RequirementFidelitySchema = Field(default_factory=RequirementFidelitySchema)
    summary: str = ""
    handoff_notes: str = ""
    confidence: float = 0.72


class CAResultSchema(BaseModel):
    shared_plan: dict[str, Any] = Field(default_factory=dict)
    interfaces: list[dict[str, Any]] = Field(default_factory=list)
    architecture_decisions: list[str] = Field(default_factory=list)
    remediation_plan: dict[str, Any] = Field(default_factory=dict)
    approval_status: str = "pending"
    summary: str = ""
    handoff_notes: str = ""
    confidence: float = 0.72


class ToolAgentSubmitPayload(BaseModel):
    summary: str
    handoff_notes: str = ""
    result_payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.72
