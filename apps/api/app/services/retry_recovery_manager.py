from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import CycleRecord, NodeExecutionRecord, RunRecord
from app.models.schemas import CycleStatus, NodeStatus, RunStatus


class RetryRecoveryManager:
    def __init__(self) -> None:
        self.settings = get_settings()

    def should_retry(self, node: NodeExecutionRecord) -> bool:
        return node.retry_count < self.settings.node_retry_limit

    def mark_node_running(self, session: Session, node: NodeExecutionRecord) -> None:
        node.status = NodeStatus.RUNNING.value
        node.error_message = None
        node.started_at = datetime.now(timezone.utc)
        session.commit()

    def mark_node_completed(self, session: Session, node: NodeExecutionRecord, result_payload: dict, handoff_notes: str) -> None:
        node.status = NodeStatus.COMPLETED.value
        node.result_payload = result_payload
        node.handoff_notes = handoff_notes
        node.finished_at = datetime.now(timezone.utc)
        session.commit()

    def mark_node_failed(self, session: Session, node: NodeExecutionRecord, error_message: str, blocked: bool) -> None:
        node.retry_count += 1
        node.status = NodeStatus.BLOCKED.value if blocked else NodeStatus.FAILED.value
        node.error_message = error_message
        node.finished_at = datetime.now(timezone.utc)
        session.commit()

    def mark_cycle_blocked(self, session: Session, run: RunRecord, cycle: CycleRecord) -> None:
        cycle.status = CycleStatus.BLOCKED.value
        run.status = RunStatus.BLOCKED.value
        session.commit()

    def prepare_resume(self, session: Session, run: RunRecord) -> CycleRecord:
        cycle = session.scalar(
            select(CycleRecord).where(CycleRecord.run_id == run.id, CycleRecord.cycle_index == run.current_cycle)
        )
        if cycle is None:
            raise ValueError("Run has no active cycle.")
        nodes = session.scalars(select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id)).all()
        for node in nodes:
            if node.status in {NodeStatus.BLOCKED.value, NodeStatus.FAILED.value}:
                node.status = NodeStatus.PENDING.value
                node.error_message = None
        cycle.status = CycleStatus.RUNNING.value
        run.status = RunStatus.RUNNING.value
        session.commit()
        return cycle
