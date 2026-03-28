from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, TypedDict


def _merge_mappings(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    if right == {}:
        return {}
    merged: dict[str, Any] = dict(left or {})
    merged.update(right or {})
    return merged


def _prefer_latest(left: Any, right: Any) -> Any:
    return right


class WorkflowState(TypedDict, total=False):
    run_id: str
    cycle_id: str
    cycle_index: int
    requirement: str
    provider_name: str
    embedding_provider_name: str
    shared_plan_id: str | None
    manual_approval: bool
    template_context: dict[str, Any]
    node_outputs: Annotated[dict[str, dict[str, Any]], _merge_mappings]
    artifact_refs: Annotated[dict[str, list[str]], _merge_mappings]
    last_completed_role: Annotated[str | None, _prefer_latest]
    next_action: str
    retry_counts: Annotated[dict[str, int], _merge_mappings]
    blocked_reason: str | None


@dataclass(slots=True)
class ExecutionBuffer:
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    result_payload: dict[str, Any] = field(default_factory=dict)
    handoff_notes: str = ""
    confidence: float = 0.72
    tool_trace: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    submitted: bool = False

    def emit_artifact(
        self,
        *,
        path: str,
        artifact_type: str,
        content_type: str,
        summary: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.artifacts.append(
            {
                "name": path.strip().lstrip("/"),
                "artifact_type": artifact_type,
                "content_type": content_type,
                "summary": summary,
                "content": content,
                "metadata": metadata or {},
            }
        )

    def submit(
        self,
        *,
        summary: str,
        handoff_notes: str,
        result_payload: dict[str, Any],
        confidence: float,
    ) -> None:
        self.summary = summary
        self.handoff_notes = handoff_notes
        self.result_payload = result_payload
        self.confidence = confidence
        self.submitted = True
