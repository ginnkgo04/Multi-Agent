from __future__ import annotations

from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.records import RunCheckpointRecord


class CheckpointStore:
    def save(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str,
        cycle_index: int,
        graph_kind: str,
        last_completed_role: str | None,
        serialized_state: dict[str, Any],
    ) -> RunCheckpointRecord:
        record = RunCheckpointRecord(
            run_id=run_id,
            cycle_id=cycle_id,
            cycle_index=cycle_index,
            graph_kind=graph_kind,
            last_completed_role=last_completed_role,
            serialized_state=serialized_state,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def latest_for_cycle(self, session: Session, *, run_id: str, cycle_id: str) -> RunCheckpointRecord | None:
        return session.scalar(
            select(RunCheckpointRecord)
            .where(
                RunCheckpointRecord.run_id == run_id,
                RunCheckpointRecord.cycle_id == cycle_id,
            )
            .order_by(desc(RunCheckpointRecord.created_at))
        )
