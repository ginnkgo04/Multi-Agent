from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.records import CycleRecord, MemoryRecord


class MemoryService:
    def add_memory(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str | None,
        memory_type: str,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        session.add(
            MemoryRecord(
                run_id=run_id,
                cycle_id=cycle_id,
                memory_type=memory_type,
                content=content,
                memory_metadata=metadata or {},
            )
        )
        session.commit()

    def list_recent(self, session: Session, run_id: str, limit: int = 6) -> list[str]:
        records = session.scalars(
            select(MemoryRecord).where(MemoryRecord.run_id == run_id).order_by(desc(MemoryRecord.created_at)).limit(limit)
        ).all()
        return [record.content for record in reversed(records)]

    def summarize_cycles(self, session: Session, run_id: str) -> list[str]:
        cycles = session.scalars(select(CycleRecord).where(CycleRecord.run_id == run_id).order_by(CycleRecord.cycle_index)).all()
        summaries = []
        for cycle in cycles:
            report = cycle.quality_report or {}
            if report:
                status = report.get("status", "UNKNOWN")
                summaries.append(f"Cycle {cycle.cycle_index}: QT={status} remediation={report.get('remediation_requirement', 'none')}")
        return summaries
