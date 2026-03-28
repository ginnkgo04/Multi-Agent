from __future__ import annotations

import asyncio
from collections import defaultdict
import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import EventRecord
from app.models.schemas import EventMessage, EventType


class EventBus:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._subscribers: dict[str, list[asyncio.Queue[EventMessage]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def publish(
        self,
        session: Session,
        *,
        run_id: str,
        event_type: EventType,
        cycle_id: str | None = None,
        node_id: str | None = None,
        payload: dict | None = None,
    ) -> EventMessage:
        next_sequence = (session.scalar(select(func.max(EventRecord.sequence)).where(EventRecord.run_id == run_id)) or 0) + 1
        record = EventRecord(
            run_id=run_id,
            sequence=next_sequence,
            event_type=event_type.value,
            cycle_id=cycle_id,
            node_id=node_id,
            payload=payload or {},
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        message = EventMessage(
            sequence=record.sequence,
            type=EventType(record.event_type),
            run_id=record.run_id,
            cycle_id=record.cycle_id,
            node_id=record.node_id,
            timestamp=record.created_at,
            payload=record.payload or {},
        )
        self._append_runtime_log(message)
        async with self._lock:
            for queue in list(self._subscribers[run_id]):
                await queue.put(message)
        return message

    async def subscribe(self, run_id: str) -> asyncio.Queue[EventMessage]:
        queue: asyncio.Queue[EventMessage] = asyncio.Queue()
        async with self._lock:
            self._subscribers[run_id].append(queue)
        return queue

    async def unsubscribe(self, run_id: str, queue: asyncio.Queue[EventMessage]) -> None:
        async with self._lock:
            if queue in self._subscribers[run_id]:
                self._subscribers[run_id].remove(queue)

    def replay(self, session: Session, run_id: str) -> list[EventMessage]:
        records = session.scalars(select(EventRecord).where(EventRecord.run_id == run_id).order_by(EventRecord.sequence)).all()
        return [
            EventMessage(
                sequence=record.sequence,
                type=EventType(record.event_type),
                run_id=record.run_id,
                cycle_id=record.cycle_id,
                node_id=record.node_id,
                timestamp=record.created_at,
                payload=record.payload or {},
            )
            for record in records
        ]

    def _append_runtime_log(self, message: EventMessage) -> None:
        log_path = self._runtime_log_path(message.run_id)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "sequence": message.sequence,
            "type": message.type.value,
            "run_id": message.run_id,
            "cycle_id": message.cycle_id,
            "node_id": message.node_id,
            "timestamp": message.timestamp.isoformat(),
            "payload": message.payload,
        }
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def _runtime_log_path(self, run_id: str) -> Path:
        return self.settings.task_root_dir / run_id / "logs" / "runtime.log"
