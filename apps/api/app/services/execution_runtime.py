from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timezone

from sqlalchemy import select

from app.db import SessionLocal
from app.models.records import CycleRecord, NodeExecutionRecord, RunRecord
from app.models.schemas import CycleStatus, EventType, NodeStatus, Role, RunStatus


class ExecutionRuntime:
    def __init__(
        self,
        *,
        registry: dict,
        provider_registry,
        graph_builder,
        context_assembler,
        artifact_store,
        event_bus,
        memory_service,
        retry_manager,
    ) -> None:
        self.registry = registry
        self.provider_registry = provider_registry
        self.graph_builder = graph_builder
        self.context_assembler = context_assembler
        self.artifact_store = artifact_store
        self.event_bus = event_bus
        self.memory_service = memory_service
        self.retry_manager = retry_manager
        self._tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def start_run(self, run_id: str, *, resumed: bool = False) -> None:
        async with self._lock:
            existing = self._tasks.get(run_id)
            if existing and not existing.done():
                return
            task = asyncio.create_task(self._run(run_id, resumed=resumed))
            self._tasks[run_id] = task
            task.add_done_callback(lambda _: self._tasks.pop(run_id, None))

    async def _run(self, run_id: str, *, resumed: bool = False) -> None:
        while True:
            with SessionLocal() as session:
                run = session.get(RunRecord, run_id)
                if run is None:
                    return
                cycle = session.scalar(
                    select(CycleRecord).where(CycleRecord.run_id == run.id, CycleRecord.cycle_index == run.current_cycle)
                )
                if cycle is None:
                    return
                run.status = RunStatus.RUNNING.value
                cycle.status = CycleStatus.RUNNING.value
                run.updated_at = datetime.now(timezone.utc)
                session.commit()
                await self.event_bus.publish(
                    session,
                    run_id=run.id,
                    event_type=EventType.RUN_RESUMED if resumed else EventType.CYCLE_STARTED,
                    cycle_id=cycle.id,
                    payload={"cycle_index": cycle.cycle_index, "status": cycle.status},
                )
                nodes, _ = self.graph_builder.ensure_cycle_nodes(session, run.id, cycle)
                batches = self._group_batches(nodes)

            blocked = False
            for batch in batches:
                tasks = [self._execute_node(run_id=run_id, cycle_id=cycle.id, node_id=node.id) for node in batch if node.status != NodeStatus.COMPLETED.value]
                if tasks:
                    await asyncio.gather(*tasks)
                with SessionLocal() as session:
                    refreshed_cycle = session.get(CycleRecord, cycle.id)
                    if refreshed_cycle and refreshed_cycle.status == CycleStatus.BLOCKED.value:
                        blocked = True
                        break
            if blocked:
                return

            with SessionLocal() as session:
                run = session.get(RunRecord, run_id)
                cycle = session.get(CycleRecord, cycle.id)
                if run is None or cycle is None:
                    return
                qt_node = session.scalar(
                    select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id, NodeExecutionRecord.role == Role.QT.value)
                )
                qt_payload = qt_node.result_payload if qt_node and qt_node.result_payload else {"status": "FAIL"}
                cycle.quality_report = qt_payload
                cycle.updated_at = datetime.now(timezone.utc)
                if qt_payload.get("status") == "FAIL":
                    cycle.status = CycleStatus.FAILED.value
                    if cycle.cycle_index >= run.max_cycles:
                        run.status = RunStatus.FAILED_MAX_CYCLES.value
                        run.updated_at = datetime.now(timezone.utc)
                        session.commit()
                        await self.event_bus.publish(
                            session,
                            run_id=run.id,
                            event_type=EventType.RUN_COMPLETED,
                            cycle_id=cycle.id,
                            payload={"status": run.status, "reason": "max_cycles_reached"},
                        )
                        return
                    remediation = qt_payload.get("remediation_requirement", "Investigate the failed quality gate and patch the implementation.")
                    next_cycle = CycleRecord(
                        run_id=run.id,
                        cycle_index=cycle.cycle_index + 1,
                        status=CycleStatus.PENDING.value,
                        remediation_requirement=remediation,
                    )
                    run.current_cycle = next_cycle.cycle_index
                    run.updated_at = datetime.now(timezone.utc)
                    session.add(next_cycle)
                    self.memory_service.add_memory(
                        session,
                        run_id=run.id,
                        cycle_id=cycle.id,
                        memory_type="qt_remediation",
                        content=f"Cycle {cycle.cycle_index} failed QT. Remediation: {remediation}",
                        metadata={"cycle_index": cycle.cycle_index},
                    )
                    session.commit()
                    await self.event_bus.publish(
                        session,
                        run_id=run.id,
                        event_type=EventType.CYCLE_REGENERATED,
                        cycle_id=next_cycle.id,
                        payload={
                            "from_cycle": cycle.cycle_index,
                            "to_cycle": next_cycle.cycle_index,
                            "remediation_requirement": remediation,
                        },
                    )
                    resumed = False
                    continue

                cycle.status = CycleStatus.COMPLETED.value
                run.status = RunStatus.COMPLETED.value
                run.updated_at = datetime.now(timezone.utc)
                session.commit()
                await self.event_bus.publish(
                    session,
                    run_id=run.id,
                    event_type=EventType.RUN_COMPLETED,
                    cycle_id=cycle.id,
                    payload={"status": run.status, "cycle_index": cycle.cycle_index},
                )
                return

    async def _execute_node(self, *, run_id: str, cycle_id: str, node_id: str) -> None:
        while True:
            with SessionLocal() as session:
                run = session.get(RunRecord, run_id)
                cycle = session.get(CycleRecord, cycle_id)
                node = session.get(NodeExecutionRecord, node_id)
                if run is None or cycle is None or node is None:
                    return
                if node.status == NodeStatus.COMPLETED.value:
                    return
                self.retry_manager.mark_node_running(session, node)
                await self.event_bus.publish(
                    session,
                    run_id=run.id,
                    event_type=EventType.NODE_STARTED,
                    cycle_id=cycle.id,
                    node_id=node.id,
                    payload={"role": node.role, "batch_index": node.batch_index, "retry_count": node.retry_count},
                )
                try:
                    chat_config, chat_provider = self.provider_registry.resolve_chat_provider(session, run.provider_name)
                    _, embedding_provider = self.provider_registry.resolve_embedding_provider(session, run.embedding_provider_name)
                    context = await self.context_assembler.build_context(
                        session,
                        run=run,
                        cycle=cycle,
                        node=node,
                        chat_config=chat_config,
                        embedding_provider=embedding_provider,
                    )
                    agent = self.registry[Role(node.role)]
                    result = await agent.execute(context, chat_provider)
                    artifacts = self.artifact_store.save_artifacts(
                        session,
                        run_id=run.id,
                        cycle_id=cycle.id,
                        cycle_index=cycle.cycle_index,
                        node_id=node.id,
                        role=node.role,
                        artifacts=result.artifact_list,
                    )
                    self.retry_manager.mark_node_completed(session, node, result.result_payload, result.handoff_notes)
                    self.memory_service.add_memory(
                        session,
                        run_id=run.id,
                        cycle_id=cycle.id,
                        memory_type=f"{node.role.lower()}_summary",
                        content=result.summary.splitlines()[0],
                        metadata={"node_id": node.id, "role": node.role},
                    )
                    await self.event_bus.publish(
                        session,
                        run_id=run.id,
                        event_type=EventType.NODE_COMPLETED,
                        cycle_id=cycle.id,
                        node_id=node.id,
                        payload={
                            "role": node.role,
                            "artifact_count": len(artifacts),
                            "result_payload": result.result_payload,
                        },
                    )
                    return
                except Exception as exc:  # noqa: BLE001
                    should_retry = self.retry_manager.should_retry(node)
                    self.retry_manager.mark_node_failed(session, node, str(exc), blocked=not should_retry)
                    await self.event_bus.publish(
                        session,
                        run_id=run.id,
                        event_type=EventType.NODE_FAILED,
                        cycle_id=cycle.id,
                        node_id=node.id,
                        payload={
                            "role": node.role,
                            "error": str(exc),
                            "will_retry": should_retry,
                            "retry_count": node.retry_count,
                        },
                    )
                    if should_retry:
                        continue
                    self.retry_manager.mark_cycle_blocked(session, run, cycle)
                    await self.event_bus.publish(
                        session,
                        run_id=run.id,
                        event_type=EventType.RUN_PAUSED,
                        cycle_id=cycle.id,
                        node_id=node.id,
                        payload={"reason": str(exc), "blocked_node": node.role},
                    )
                    return

    @staticmethod
    def _group_batches(nodes: list[NodeExecutionRecord]) -> list[list[NodeExecutionRecord]]:
        grouped: dict[int, list[NodeExecutionRecord]] = {}
        for node in nodes:
            grouped.setdefault(node.batch_index, []).append(node)
        return [grouped[index] for index in sorted(grouped)]

    async def shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
