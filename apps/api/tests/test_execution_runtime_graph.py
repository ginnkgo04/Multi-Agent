import asyncio

import pytest

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
