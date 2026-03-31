from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any, cast

from sqlalchemy import select

from app.agents.base import WorkflowAgent
from app.agents.runtime_types import WorkflowState
from app.db import SessionLocal
from app.models.records import CycleRecord, NodeExecutionRecord, RunRecord
from app.models.schemas import CycleStatus, EventType, NodeStatus, Role, RunStatus
from app.services.workflow_graph_builder import role_dependencies_for_cycle


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
        rag_service,
        context_document_service=None,
        checkpoint_store=None,
    ) -> None:
        self.registry = registry
        self.provider_registry = provider_registry
        self.graph_builder = graph_builder
        self.context_assembler = context_assembler
        self.artifact_store = artifact_store
        self.event_bus = event_bus
        self.memory_service = memory_service
        self.retry_manager = retry_manager
        self.rag_service = rag_service
        self.context_document_service = context_document_service or rag_service
        self.checkpoint_store = checkpoint_store
        self._tasks: dict[str, asyncio.Task] = {}
        self._graphs: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def start_run(self, run_id: str, *, resumed: bool = False, force_restart: bool = False) -> None:
        async with self._lock:
            existing = self._tasks.get(run_id)
            if existing and not existing.done():
                if not force_restart:
                    return
                existing.cancel()
                with suppress(asyncio.CancelledError):
                    await existing
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
                self.graph_builder.ensure_cycle_nodes(session, run.id, cycle)
                graph_kind, state = self._hydrate_state(session, run, cycle)
                graph = self._compile_graph(graph_kind)

            try:
                final_state = await graph.ainvoke(state)
            except Exception as exc:  # noqa: BLE001
                with SessionLocal() as session:
                    run = session.get(RunRecord, run_id)
                    cycle = session.get(CycleRecord, cycle.id)
                    if run is None or cycle is None:
                        return
                    if run.status != RunStatus.BLOCKED.value:
                        self.retry_manager.mark_cycle_blocked(session, run, cycle)
                        await self.event_bus.publish(
                            session,
                            run_id=run.id,
                            event_type=EventType.RUN_PAUSED,
                            cycle_id=cycle.id,
                            payload={"reason": str(exc), "blocked_node": state.get("last_completed_role")},
                        )
                return

            if final_state.get("next_action") == "continue":
                resumed = False
                continue
            with SessionLocal() as session:
                run = session.get(RunRecord, run_id)
                cycle = session.get(CycleRecord, cycle.id)
                if run is None or cycle is None:
                    return
                await self.event_bus.publish(
                    session,
                    run_id=run.id,
                    event_type=EventType.RUN_COMPLETED,
                    cycle_id=cycle.id,
                    payload={"status": run.status, "cycle_index": cycle.cycle_index},
                )
            return

    def _hydrate_state(self, session, run: RunRecord, cycle: CycleRecord) -> tuple[str, WorkflowState]:
        checkpoint = self.checkpoint_store.latest_for_cycle(session, run_id=run.id, cycle_id=cycle.id) if self.checkpoint_store else None
        graph_kind = checkpoint.graph_kind if checkpoint else ("initial" if cycle.cycle_index == 1 else "remediation")
        if checkpoint:
            state: WorkflowState = dict(checkpoint.serialized_state or {})  # type: ignore
            state["run_id"] = run.id
            state["cycle_id"] = cycle.id
            state["cycle_index"] = cycle.cycle_index
            state["requirement"] = run.requirement
            state["provider_name"] = run.provider_name
            state["embedding_provider_name"] = run.embedding_provider_name
            state["manual_approval"] = run.manual_approval
            state["template_context"] = run.template_context or {}
            state["template_context_origin"] = run.template_context_origin
            return graph_kind, state
        return graph_kind, {
            "run_id": run.id,
            "cycle_id": cycle.id,
            "cycle_index": cycle.cycle_index,
            "requirement": run.requirement,
            "provider_name": run.provider_name,
            "embedding_provider_name": run.embedding_provider_name,
            "shared_plan_id": None,
            "manual_approval": run.manual_approval,
            "template_context": run.template_context or {},
            "template_context_origin": run.template_context_origin,
            "node_outputs": {},
            "artifact_refs": {},
            "last_completed_role": None,
            "next_action": "pending",
            "retry_counts": {},
            "blocked_reason": None,
        }

    def _compile_graph(self, graph_kind: str):
        if graph_kind in self._graphs:
            return self._graphs[graph_kind]
        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError as exc:  # pragma: no cover - depends on optional packages
            raise RuntimeError("LangGraph is not installed. Install langgraph to run the workflow runtime.") from exc

        initial = graph_kind == "initial"
        role_order = [Role.PC, Role.CA, Role.FD, Role.BD, Role.DE, Role.QT] if initial else [Role.CA, Role.FD, Role.BD, Role.DE, Role.QT]
        graph = StateGraph(WorkflowState)
        role_dependencies = role_dependencies_for_cycle(1 if initial else 2)
        for role in role_order:
            graph.add_node(role.value, self._build_role_node(role, graph_kind))
        graph.add_node("cycle_transition", self._transition_cycle)
        graph.add_edge(START, role_order[0].value)
        for role in role_order:
            for dependency in role_dependencies[role]:
                if dependency in role_order:
                    graph.add_edge(dependency.value, role.value)
        graph.add_conditional_edges(Role.QT.value, self._route_after_qt, {"complete": END, "transition": "cycle_transition"})
        graph.add_edge("cycle_transition", END)
        compiled = graph.compile()
        self._graphs[graph_kind] = compiled
        return compiled

    def _build_role_node(self, role: Role, graph_kind: str):
        async def runner(state: WorkflowState) -> WorkflowState:
            if role.value in (state.get("node_outputs") or {}):
                return {}
            return await self._execute_role(state, role, graph_kind)

        return runner

    async def _execute_role(self, state: WorkflowState, role: Role, graph_kind: str) -> WorkflowState:
        while True:
            run_id = state.get("run_id")
            cycle_id = state.get("cycle_id")
            if run_id is None or cycle_id is None:
                raise ValueError("Workflow state is missing run_id or cycle_id.")
            with SessionLocal() as session:
                run = session.get(RunRecord, run_id)
                cycle = session.get(CycleRecord, cycle_id)
                node = session.scalar(
                    select(NodeExecutionRecord).where(
                        NodeExecutionRecord.cycle_id == cycle_id,
                        NodeExecutionRecord.role == role.value,
                    )
                )
                if run is None or cycle is None or node is None:
                    raise ValueError("Workflow node could not be loaded from the database.")
                assert run is not None and cycle is not None and node is not None
                run_event_id = run.id
                cycle_event_id = cycle.id
                node_event_id = node.id
                node_role = node.role
                if run_event_id is None or cycle_event_id is None or node_event_id is None or node_role is None:
                    raise ValueError("Workflow node identity fields are missing.")
                if node.status == NodeStatus.COMPLETED.value:
                    return self._sync_state_from_node(state, node, cycle)
                self.retry_manager.mark_node_running(session, node)
                await self.event_bus.publish(
                    session,
                    run_id=run.id,
                    event_type=EventType.NODE_STARTED,
                    cycle_id=cycle.id,
                    node_id=node.id,
                    payload={"role": node.role, "graph_kind": graph_kind, "retry_count": node.retry_count},
                )
                try:
                    fallback_provider = None
                    if role in {Role.PC, Role.CA}:
                        chat_config, chat_model = self.provider_registry.resolve_chat_provider(session, run.provider_name)
                    else:
                        chat_config, chat_model = self.provider_registry.resolve_langchain_chat_model(session, run.provider_name)
                        _, fallback_provider = self.provider_registry.resolve_chat_provider(session, run.provider_name)
                    _, embedding_model = self.provider_registry.resolve_embedding_provider(session, run.embedding_provider_name)
                    await self.event_bus.publish(
                        session,
                        run_id=run.id,
                        event_type=EventType.NODE_LOG,
                        cycle_id=cycle.id,
                        node_id=node.id,
                        payload={
                            "role": node.role,
                            "tool_name": "provider_resolution",
                            "status": "ok",
                            "provider_name": run.provider_name,
                            "provider_kind": "native" if role in {Role.PC, Role.CA} else "langchain",
                            "chat_model_class": type(chat_model).__name__,
                            "chat_model_module": type(chat_model).__module__,
                            "fallback_provider_class": type(fallback_provider).__name__ if fallback_provider is not None else None,
                            "embedding_provider_name": run.embedding_provider_name,
                            "embedding_model_class": type(embedding_model).__name__,
                            "embedding_model_module": type(embedding_model).__module__,
                        },
                    )
                    context = await self.context_assembler.build_context(
                        session,
                        run=run,
                        cycle=cycle,
                        node=node,
                        chat_config=chat_config,
                        embedding_provider=embedding_model,
                    )
                    await self.event_bus.publish(
                        session,
                        run_id=run_event_id,
                        event_type=EventType.CONTEXT_ASSEMBLED,
                        cycle_id=cycle_event_id,
                        node_id=node_event_id,
                        payload={
                            "role": node_role,
                            "context_sources": [source.model_dump(mode="json") for source in context.context_sources],
                            "metadata": context.context_metadata,
                        },
                    )

                    async def tool_logger(tool_name: str, status: str, payload: dict[str, Any] | None = None) -> None:
                        await self.event_bus.publish(
                            session,
                            run_id=run_event_id,
                            event_type=EventType.NODE_LOG,
                            cycle_id=cycle_event_id,
                            node_id=node_event_id,
                            payload={
                                "role": node_role,
                                "tool_name": tool_name,
                                "status": status,
                                **(payload or {}),
                            },
                        )

                    agent = self.registry[role]
                    result = await agent.execute(
                        context,
                        chat_model=chat_model,
                        fallback_provider=fallback_provider,
                        session=session,
                        embedding_model=embedding_model,
                        rag_service=self.rag_service,
                        tool_logger=tool_logger,
                    )
                    artifacts = self.artifact_store.save_artifacts(
                        session,
                        run_id=run.id,
                        cycle_id=cycle.id,
                        cycle_index=cycle.cycle_index,
                        node_id=node.id,
                        role=node.role,
                        artifacts=result.artifact_list,
                    )
                    indexed_artifacts = await self.context_document_service.index_artifacts(
                        session,
                        project_id=run.project_id,
                        artifacts=artifacts,
                        embedding_provider=embedding_model,
                    )
                    if indexed_artifacts:
                        await self.event_bus.publish(
                            session,
                            run_id=run.id,
                            event_type=EventType.CONTEXT_INDEXED,
                            cycle_id=cycle.id,
                            node_id=node.id,
                            payload={
                                "role": node.role,
                                "source_type": "artifact",
                                "chunk_count": indexed_artifacts,
                            },
                        )
                    shared_plan_id = await self._sync_shared_plan(
                        session=session,
                        run=run,
                        cycle=cycle,
                        node=node,
                        result_payload=result.result_payload,
                        summary=result.summary,
                        embedding_model=embedding_model,
                    )
                    node.context_snapshot = {
                        "context_sources": [source.model_dump(mode="json") for source in context.context_sources],
                        "metadata": context.context_metadata,
                    }
                    self.retry_manager.mark_node_completed(session, node, result.result_payload, result.handoff_notes)
                    self.memory_service.add_memory(
                        session,
                        run_id=run.id,
                        cycle_id=cycle.id,
                        memory_type=f"{node.role.lower()}_summary",
                        content=result.summary.splitlines()[0],
                        metadata={"node_id": node.id, "role": node.role},
                    )
                    await self._sync_memory_summaries(
                        session=session,
                        run=run,
                        cycle=cycle,
                        node=node,
                        result_payload=result.result_payload,
                        embedding_model=embedding_model,
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
                    state_update = self._next_state(
                        state,
                        role=role,
                        cycle=cycle,
                        node=node,
                        shared_plan_id=shared_plan_id,
                        result_payload=result.result_payload,
                        artifacts=artifacts,
                    )
                    checkpoint_state = self._merge_state(state, state_update)
                    await self._save_checkpoint(session, checkpoint_state, graph_kind)
                    return state_update
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
                    raise

    async def _transition_cycle(self, state: WorkflowState) -> WorkflowState:
        run_id = state.get("run_id")
        cycle_id = state.get("cycle_id")
        if run_id is None or cycle_id is None:
            raise ValueError("Workflow state is missing run_id or cycle_id.")
        with SessionLocal() as session:
            run = session.get(RunRecord, run_id)
            cycle = session.get(CycleRecord, cycle_id)
            if run is None or cycle is None:
                raise ValueError("Workflow transition could not load run state.")
            qt_node = session.scalar(
                select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id, NodeExecutionRecord.role == Role.QT.value)
            )
            qt_payload = qt_node.result_payload if qt_node and qt_node.result_payload else {"status": "FAIL"}
            remediation = qt_payload.get(
                "remediation_requirement",
                "Investigate the failed quality gate and patch the implementation.",
            )
            next_cycle = CycleRecord(
                run_id=run.id,
                cycle_index=cycle.cycle_index + 1,
                status=CycleStatus.PENDING.value,
                remediation_requirement=remediation,
            )
            session.add(next_cycle)
            run.current_cycle = next_cycle.cycle_index
            run.updated_at = datetime.now(timezone.utc)
            self.memory_service.add_memory(
                session,
                run_id=run.id,
                cycle_id=cycle.id,
                memory_type="qt_remediation",
                content=f"Cycle {cycle.cycle_index} failed QT. Remediation: {remediation}",
                metadata={"cycle_index": cycle.cycle_index},
            )
            session.commit()
            session.refresh(next_cycle)
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
            state_update: WorkflowState = {
                "cycle_id": next_cycle.id,
                "cycle_index": next_cycle.cycle_index,
                "last_completed_role": None,
                "next_action": "continue",
                "blocked_reason": None,
                "node_outputs": {},
                "artifact_refs": {},
                "retry_counts": {},
                "shared_plan_id": None,
            }
            checkpoint_state = self._merge_state(state, state_update)
            await self._save_checkpoint(session, checkpoint_state, "remediation")
            return state_update

    def _route_after_qt(self, state: WorkflowState) -> str:
        return "transition" if state.get("next_action") == "continue" else "complete"

    @staticmethod
    def _qt_requires_remediation(result_payload: dict[str, Any]) -> bool:
        defects = WorkflowAgent._normalize_quality_defect_list(result_payload.get("defect_list", []))
        status = WorkflowAgent._normalize_quality_status(result_payload.get("status", "FAIL"), defects)
        return status == "FAIL"

    def _next_state(
        self,
        state: WorkflowState,
        *,
        role: Role,
        cycle: CycleRecord,
        node: NodeExecutionRecord,
        shared_plan_id: str | None,
        result_payload: dict[str, Any],
        artifacts,
    ) -> WorkflowState:
        state_update: WorkflowState = {
            "node_outputs": {role.value: result_payload},
            "artifact_refs": {role.value: [artifact.id for artifact in artifacts]},
            "last_completed_role": role.value,
            "retry_counts": {role.value: node.retry_count},
        }
        if shared_plan_id:
            state_update["shared_plan_id"] = shared_plan_id

        if role is not Role.QT:
            return state_update

        defects = WorkflowAgent._normalize_quality_defect_list(result_payload.get("defect_list", []))
        status = WorkflowAgent._normalize_quality_status(result_payload.get("status", "FAIL"), defects)
        result_payload = {
            **result_payload,
            "status": status,
            "defect_list": defects,
        }
        state_update["next_action"] = "complete"
        run_id = state.get("run_id")
        if run_id is None:
            return state_update
        with SessionLocal() as session:
            run = session.get(RunRecord, run_id)
            current_cycle = session.get(CycleRecord, cycle.id)
            if run is None or current_cycle is None:
                return state_update
            current_cycle.quality_report = result_payload
            current_cycle.updated_at = datetime.now(timezone.utc)
            if self._qt_requires_remediation(result_payload):
                current_cycle.status = CycleStatus.FAILED.value
                if current_cycle.cycle_index >= run.max_cycles:
                    run.status = RunStatus.FAILED_MAX_CYCLES.value
                    run.updated_at = datetime.now(timezone.utc)
                else:
                    state_update["next_action"] = "continue"
                session.commit()
            else:
                current_cycle.status = CycleStatus.COMPLETED.value
                run.status = RunStatus.COMPLETED.value
                run.updated_at = datetime.now(timezone.utc)
                session.commit()
        return state_update

    def _sync_state_from_node(self, state: WorkflowState, node: NodeExecutionRecord, cycle: CycleRecord) -> WorkflowState:
        state_update: WorkflowState = {
            "node_outputs": {node.role: node.result_payload or {}},
            "retry_counts": {node.role: node.retry_count},
            "last_completed_role": node.role,
        }
        if node.role in {Role.PC.value, Role.CA.value}:
            with SessionLocal() as session:
                shared_plan = self.context_document_service.get_current_shared_plan(session, state.get("run_id"))
                if shared_plan is not None:
                    state_update["shared_plan_id"] = shared_plan.id
        if node.role == Role.QT.value:
            state_update["next_action"] = "continue" if self._qt_requires_remediation(node.result_payload or {}) else "complete"
        return state_update

    def _merge_state(self, base_state: WorkflowState, state_update: WorkflowState) -> WorkflowState:
        merged: WorkflowState = cast(WorkflowState, dict(base_state))
        for key, value in state_update.items():
            if key in {"node_outputs", "artifact_refs", "retry_counts"}:
                if value == {}:
                    merged[key] = {}
                    continue
                merged[key] = {
                    **dict(merged.get(key, {})),
                    **dict(value if isinstance(value, dict) else {}),
                }
            else:
                merged[key] = value
        return merged

    async def _save_checkpoint(self, session, state: WorkflowState, graph_kind: str) -> None:
        if self.checkpoint_store is None:
            return
        run_id = state.get("run_id")
        cycle_id = state.get("cycle_id")
        cycle_index = state.get("cycle_index")
        if run_id is None or cycle_id is None or cycle_index is None:
            raise ValueError("Workflow state is missing checkpoint identity fields.")
        record = self.checkpoint_store.save(
            session,
            run_id=run_id,
            cycle_id=cycle_id,
            cycle_index=cycle_index,
            graph_kind=graph_kind,
            last_completed_role=state.get("last_completed_role"),
            serialized_state=dict(state),
        )
        await self.event_bus.publish(
            session,
            run_id=run_id,
            event_type=EventType.CHECKPOINT_SAVED,
            cycle_id=cycle_id,
            payload={
                "checkpoint_id": record.id,
                "graph_kind": graph_kind,
                "last_completed_role": state.get("last_completed_role"),
            },
        )

    async def _sync_shared_plan(
        self,
        *,
        session,
        run: RunRecord,
        cycle: CycleRecord,
        node: NodeExecutionRecord,
        result_payload: dict[str, Any],
        summary: str,
        embedding_model,
    ) -> str | None:
        plan_payload: dict[str, Any] | None = None
        if node.role == Role.PC.value:
            plan_payload = {
                "requirement_brief": result_payload.get("requirement_brief", ""),
                "acceptance_criteria": result_payload.get("acceptance_criteria", {}),
                "work_breakdown": result_payload.get("work_breakdown", []),
                "template_context": run.template_context or {},
            }
        elif node.role == Role.CA.value and result_payload.get("shared_plan"):
            plan_payload = dict(result_payload.get("shared_plan") or {})
            plan_payload.setdefault("interfaces", result_payload.get("interfaces", []))
            plan_payload.setdefault("architecture_decisions", result_payload.get("architecture_decisions", []))
            plan_payload.setdefault("template_context", run.template_context or {})
        if not plan_payload:
            return None
        shared_plan = self.context_document_service.create_shared_plan(
            session,
            run_id=run.id,
            cycle_id=cycle.id,
            produced_by_role=node.role,
            plan_payload=plan_payload,
            summary=summary,
        )
        indexed = await self.context_document_service.index_shared_plan(
            session,
            project_id=run.project_id,
            record=shared_plan,
            embedding_provider=embedding_model,
        )
        await self.event_bus.publish(
            session,
            run_id=run.id,
            event_type=EventType.CONTEXT_INDEXED,
            cycle_id=cycle.id,
            node_id=node.id,
            payload={
                "role": node.role,
                "source_type": "shared_plan",
                "source_id": shared_plan.id,
                "chunk_count": indexed,
            },
        )
        return shared_plan.id

    async def _sync_memory_summaries(
        self,
        *,
        session,
        run: RunRecord,
        cycle: CycleRecord,
        node: NodeExecutionRecord,
        result_payload: dict[str, Any],
        embedding_model,
    ) -> None:
        if node.role != Role.QT.value:
            return
        summary_content, metadata = self.memory_service.build_cycle_summary(
            session,
            run_id=run.id,
            cycle_id=cycle.id,
            cycle_index=cycle.cycle_index,
            qt_payload=result_payload,
        )
        cycle_summary = self.memory_service.create_summary(
            session,
            run_id=run.id,
            project_id=run.project_id,
            cycle_id=cycle.id,
            summary_type="cycle_summary",
            content=summary_content,
            metadata=metadata,
        )
        indexed_cycle = await self.context_document_service.index_memory_summary(
            session,
            record=cycle_summary,
            embedding_provider=embedding_model,
        )
        await self.event_bus.publish(
            session,
            run_id=run.id,
            event_type=EventType.CONTEXT_INDEXED,
            cycle_id=cycle.id,
            node_id=node.id,
            payload={
                "role": node.role,
                "source_type": "memory",
                "summary_type": "cycle_summary",
                "source_id": cycle_summary.id,
                "chunk_count": indexed_cycle,
            },
        )
        if str(result_payload.get("status", "FAIL")).upper() != "PASS":
            return
        profile = self.memory_service.upsert_project_template_profile(
            session,
            project_id=run.project_id,
            run=run,
            cycle_id=cycle.id,
        )
        indexed_profile = await self.context_document_service.index_memory_summary(
            session,
            record=profile,
            embedding_provider=embedding_model,
        )
        await self.event_bus.publish(
            session,
            run_id=run.id,
            event_type=EventType.CONTEXT_INDEXED,
            cycle_id=cycle.id,
            node_id=node.id,
            payload={
                "role": node.role,
                "source_type": "memory",
                "summary_type": "project_template_profile",
                "source_id": profile.id,
                "chunk_count": indexed_profile,
            },
        )

    async def shutdown(self) -> None:
        for task in list(self._tasks.values()):
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
