import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.services.execution_runtime as execution_runtime_module
from app.db import Base
from app.models.records import CycleRecord, NodeExecutionRecord, ProjectRecord, RunRecord
from app.models.schemas import AgentTaskResult, EditOperation, Role
from app.services.retry_recovery_manager import RetryRecoveryManager
from app.services.execution_runtime import ExecutionRuntime

pytest.importorskip("langgraph", reason="langgraph not installed")


class Stub:
    pass


def test_compile_graph_caches_initial_and_remediation_graphs() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    first_initial = runtime._compile_graph("initial")
    second_initial = runtime._compile_graph("initial")
    remediation = runtime._compile_graph("remediation")

    assert first_initial is second_initial
    assert remediation is runtime._graphs["remediation"]


def test_merge_state_combines_parallel_branch_updates() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )
    base_state = {
        "run_id": "run-1",
        "cycle_id": "cycle-1",
        "cycle_index": 1,
        "node_outputs": {"CA": {"shared_plan": {"steps": ["fd", "bd"]}}},
        "artifact_refs": {},
        "retry_counts": {},
        "next_action": "pending",
    }

    merged = runtime._merge_state(
        base_state,
        {
            "node_outputs": {"FD": {"implemented_features": ["dashboard"]}},
            "artifact_refs": {"FD": ["artifact-1"]},
            "retry_counts": {"FD": 0},
            "last_completed_role": "FD",
        },
    )

    assert merged["run_id"] == "run-1"
    assert merged["node_outputs"]["CA"]["shared_plan"]["steps"] == ["fd", "bd"]
    assert merged["node_outputs"]["FD"]["implemented_features"] == ["dashboard"]
    assert merged["artifact_refs"]["FD"] == ["artifact-1"]


def test_merge_state_clears_cycle_scoped_mappings_when_transition_resets_them() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )
    base_state = {
        "run_id": "run-1",
        "cycle_id": "cycle-1",
        "cycle_index": 1,
        "node_outputs": {
            "PC": {"requirement_brief": "brief"},
            "QT": {"status": "FAIL"},
        },
        "artifact_refs": {"FD": ["artifact-1"]},
        "retry_counts": {"FD": 2},
        "next_action": "continue",
    }

    merged = runtime._merge_state(
        base_state,
        {
            "cycle_id": "cycle-2",
            "cycle_index": 2,
            "node_outputs": {},
            "artifact_refs": {},
            "retry_counts": {},
            "last_completed_role": None,
            "shared_plan_id": None,
            "next_action": "continue",
        },
    )

    assert merged["cycle_id"] == "cycle-2"
    assert merged["cycle_index"] == 2
    assert merged["node_outputs"] == {}
    assert merged["artifact_refs"] == {}
    assert merged["retry_counts"] == {}


def test_quality_gate_requires_remediation_when_high_severity_defect_exists() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    assert runtime._qt_requires_remediation(
        {
            "status": "PASS",
            "defect_list": [
                {"id": "QT-001", "description": "Missing contact form", "severity": "high"},
            ],
        }
    )
    assert not runtime._qt_requires_remediation(
        {
            "status": "PASS",
            "defect_list": [
                {"id": "QT-002", "description": "Minor alt issue", "severity": "low"},
            ],
        }
    )


def test_quality_gate_requires_approval_for_high_severity_or_explicit_recommendation() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    assert runtime._qt_requires_approval(
        {
            "status": "FAIL",
            "defect_list": [
                {"id": "QT-001", "description": "Missing auth", "severity": "high"},
            ],
        }
    )
    assert runtime._qt_requires_approval(
        {
            "status": "FAIL",
            "approval_recommended": True,
            "defect_list": [
                {"id": "QT-002", "description": "Needs review", "severity": "medium"},
            ],
        }
    )
    assert not runtime._qt_requires_approval(
        {
            "status": "FAIL",
            "defect_list": [
                {"id": "QT-003", "description": "Minor copy issue", "severity": "low"},
            ],
        }
    )


def test_pc_requires_clarification_when_model_flags_ambiguity_or_low_fidelity() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    assert runtime._pc_requires_clarification(
        {
            "intent": {
                "needs_clarification": True,
                "clarifying_questions": ["Should this be a landing page or dashboard?"],
            },
            "requirement_fidelity": {
                "semantic_coverage_score": 0.95,
                "constraint_retention_score": 0.96,
            },
        }
    )
    assert runtime._pc_requires_clarification(
        {
            "intent": {
                "needs_clarification": False,
                "clarifying_questions": [],
            },
            "requirement_fidelity": {
                "semantic_coverage_score": 0.82,
                "constraint_retention_score": 0.94,
            },
        }
    )
    assert not runtime._pc_requires_clarification(
        {
            "intent": {
                "needs_clarification": False,
                "clarifying_questions": [],
            },
            "requirement_fidelity": {
                "semantic_coverage_score": 0.91,
                "constraint_retention_score": 0.95,
            },
        }
    )


def test_ca_requires_approval_for_initial_cycle_or_severe_remediation() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    assert runtime._ca_requires_approval({"cycle_index": 1, "approval_required": False})
    assert runtime._ca_requires_approval({"cycle_index": 2, "approval_required": True})
    assert not runtime._ca_requires_approval({"cycle_index": 2, "approval_required": False})


@pytest.mark.anyio
async def test_start_run_can_force_restart_existing_task() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    started: list[tuple[str, bool]] = []

    async def fake_run(run_id: str, *, resumed: bool = False) -> None:
        started.append((run_id, resumed))
        await asyncio.sleep(10)

    runtime._run = fake_run  # type: ignore[method-assign]

    await runtime.start_run("run-1")
    await asyncio.sleep(0)
    first_task = runtime._tasks["run-1"]
    await runtime.start_run("run-1", resumed=True, force_restart=True)
    await asyncio.sleep(0)
    second_task = runtime._tasks["run-1"]

    assert first_task is not second_task
    assert started[0] == ("run-1", False)
    assert started[1] == ("run-1", True)

    second_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await second_task


@pytest.mark.anyio
async def test_clarification_gate_allows_pc_defaults_already_accepted() -> None:
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    gate = runtime._build_clarification_gate("initial")
    state_update = await gate(
        {
            "run_id": "run-1",
            "cycle_id": "cycle-1",
            "cycle_index": 1,
            "clarification_accepted_target_role": "PC",
            "node_outputs": {
                "PC": {
                    "intent": {
                        "needs_clarification": True,
                        "clarifying_questions": ["Who is the page for?"],
                    },
                    "requirement_fidelity": {
                        "semantic_coverage_score": 0.7,
                        "constraint_retention_score": 0.8,
                        "clarification_needed": True,
                    },
                }
            },
        }
    )

    assert state_update["next_action"] == "continue"
    assert state_update["clarification_accepted_target_role"] is None


@pytest.mark.anyio
async def test_recover_inflight_runs_requeues_orphaned_running_nodes(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
    created_at = datetime.now(timezone.utc)
    with testing_session_local() as session:
        session.add(ProjectRecord(id="project-1", name="Demo", description="Demo", created_at=created_at))
        session.add(
            RunRecord(
                id="run-1",
                project_id="project-1",
                requirement="Build a sakura page",
                status="RUNNING",
                current_cycle=1,
                max_cycles=3,
                provider_name="openai",
                embedding_provider_name="Qwen",
                manual_approval=False,
                template_context={},
                template_context_origin="explicit",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            CycleRecord(
                id="cycle-1",
                run_id="run-1",
                cycle_index=1,
                status="RUNNING",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            NodeExecutionRecord(
                id="node-1",
                run_id="run-1",
                cycle_id="cycle-1",
                role="PC",
                batch_index=0,
                status="RUNNING",
                retry_count=0,
                task_spec={},
            )
        )
        session.commit()

    monkeypatch.setattr(execution_runtime_module, "SessionLocal", testing_session_local)
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=RetryRecoveryManager(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    resumed_calls: list[tuple[str, bool, bool]] = []

    async def fake_start_run(run_id: str, *, resumed: bool = False, force_restart: bool = False) -> None:
        resumed_calls.append((run_id, resumed, force_restart))

    runtime.start_run = fake_start_run  # type: ignore[method-assign]

    recovered = await runtime.recover_inflight_runs()

    assert recovered == ["run-1"]
    assert resumed_calls == [("run-1", True, True)]
    with testing_session_local() as session:
        run = session.get(RunRecord, "run-1")
        cycle = session.get(CycleRecord, "cycle-1")
        node = session.scalar(select(NodeExecutionRecord).where(NodeExecutionRecord.id == "node-1"))

    assert run is not None and run.status == "RUNNING"
    assert cycle is not None and cycle.status == "RUNNING"
    assert node is not None and node.status == "PENDING"
    assert node.error_message is None


def test_fd_completion_does_not_overwrite_quality_report(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )
    created_at = datetime.now(timezone.utc)
    with testing_session_local() as session:
        session.add(ProjectRecord(id="project-1", name="Demo", description="Demo", created_at=created_at))
        session.add(
            RunRecord(
                id="run-1",
                project_id="project-1",
                requirement="Build a sakura page",
                status="RUNNING",
                current_cycle=1,
                max_cycles=3,
                provider_name="openai",
                embedding_provider_name="Qwen",
                manual_approval=False,
                template_context={},
                template_context_origin="explicit",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            CycleRecord(
                id="cycle-1",
                run_id="run-1",
                cycle_index=1,
                status="RUNNING",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            NodeExecutionRecord(
                id="node-fd",
                run_id="run-1",
                cycle_id="cycle-1",
                role="FD",
                batch_index=2,
                status="COMPLETED",
                retry_count=0,
                task_spec={},
                result_payload={"implemented_features": ["hero", "gallery"]},
            )
        )
        session.commit()
        cycle = session.get(CycleRecord, "cycle-1")
        node = session.get(NodeExecutionRecord, "node-fd")

    monkeypatch.setattr(execution_runtime_module, "SessionLocal", testing_session_local)
    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=Stub(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=RetryRecoveryManager(),
        rag_service=Stub(),
        checkpoint_store=Stub(),
    )

    fd_payload = {"implemented_features": ["hero", "gallery"]}
    state_update = runtime._next_state(
        {"run_id": "run-1"},
        role=Role.FD,
        cycle=cycle,
        node=node,
        shared_plan_id=None,
        result_payload=fd_payload,
        artifacts=[],
    )

    with testing_session_local() as session:
        refreshed_cycle = session.get(CycleRecord, "cycle-1")

    assert state_update["node_outputs"]["FD"] == fd_payload
    assert "next_action" not in state_update
    assert refreshed_cycle is not None and refreshed_cycle.quality_report is None
    assert refreshed_cycle is not None and refreshed_cycle.status == "RUNNING"


@pytest.mark.anyio
async def test_persist_role_outputs_passes_edit_operations_to_artifact_store() -> None:
    captured: dict[str, object] = {}

    class ArtifactStoreSpy:
        def save_role_outputs(self, session, **kwargs):  # noqa: ANN001
            captured["artifact_names"] = [artifact["name"] for artifact in kwargs["artifacts"]]
            captured["edit_paths"] = [operation.path for operation in kwargs["edit_operations"]]
            return []

    runtime = ExecutionRuntime(
        registry={},
        provider_registry=Stub(),
        graph_builder=Stub(),
        context_assembler=Stub(),
        artifact_store=ArtifactStoreSpy(),
        event_bus=Stub(),
        memory_service=Stub(),
        retry_manager=Stub(),
        rag_service=Stub(),
        context_document_service=SimpleNamespace(index_artifacts=AsyncMock(return_value=0)),
        checkpoint_store=Stub(),
    )

    result = AgentTaskResult(
        summary="Updated the frontend workspace.",
        artifact_list=[
            {
                "name": "implementation/frontend/notes.md",
                "artifact_type": "documentation",
                "content_type": "text/markdown",
                "summary": "Frontend notes",
                "content": "# Notes\n",
            }
        ],
        edit_operations=[
            EditOperation(
                path="workspace/frontend/app/page.tsx",
                operation="update",
                strategy="replace",
                summary="Update the hero copy",
                old_text="Polar Bear",
                new_text="Arctic Fox",
            )
        ],
        result_payload={"implemented_features": ["hero copy refresh"]},
        confidence=0.8,
        handoff_notes="QT can validate the updated page.",
    )

    await runtime._persist_role_outputs(
        session=None,
        run=SimpleNamespace(id="run-1", project_id="project-1"),
        cycle=SimpleNamespace(id="cycle-2", cycle_index=2),
        node=SimpleNamespace(id="node-fd", role=Role.FD.value),
        result=result,
        embedding_model=SimpleNamespace(),
    )

    assert captured["artifact_names"] == ["implementation/frontend/notes.md"]
    assert captured["edit_paths"] == ["workspace/frontend/app/page.tsx"]
