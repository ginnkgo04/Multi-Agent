from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.records import CycleRecord, NodeExecutionRecord, ProjectRecord, RunRecord
from app.models.schemas import CycleStatus, NodeStatus, Role, RunStatus
from app.services.retry_recovery_manager import RetryRecoveryManager


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    return local_session()


def test_prepare_resume_rejects_completed_run() -> None:
    manager = RetryRecoveryManager()
    run = SimpleNamespace(status=RunStatus.COMPLETED.value)

    with pytest.raises(ValueError, match="Only blocked or running runs can be restarted."):
        manager.prepare_resume(None, run)  # type: ignore[arg-type]


def test_prepare_resume_rejects_waiting_approval_run() -> None:
    manager = RetryRecoveryManager()
    run = SimpleNamespace(status=RunStatus.WAITING_APPROVAL.value)

    with pytest.raises(ValueError, match="Only blocked or running runs can be restarted."):
        manager.prepare_resume(None, run)  # type: ignore[arg-type]


def test_prepare_resume_rejects_waiting_clarification_run() -> None:
    manager = RetryRecoveryManager()
    run = SimpleNamespace(status=RunStatus.WAITING_CLARIFICATION.value)

    with pytest.raises(ValueError, match="Only blocked or running runs can be restarted."):
        manager.prepare_resume(None, run)  # type: ignore[arg-type]


def test_prepare_resume_resets_blocked_node_retry_budget() -> None:
    session = make_session()
    project = ProjectRecord(name="Demo")
    session.add(project)
    session.commit()
    session.refresh(project)
    run = RunRecord(
        project_id=project.id,
        requirement="Build a page",
        status=RunStatus.BLOCKED.value,
        current_cycle=1,
        provider_name="chat",
        embedding_provider_name="embed",
    )
    session.add(run)
    session.flush()
    cycle = CycleRecord(run_id=run.id, cycle_index=1, status=CycleStatus.BLOCKED.value)
    session.add(cycle)
    session.flush()
    node = NodeExecutionRecord(
        run_id=run.id,
        cycle_id=cycle.id,
        role=Role.BD.value,
        batch_index=1,
        status=NodeStatus.BLOCKED.value,
        retry_count=6,
        error_message="Server disconnected without sending a response.",
    )
    session.add(node)
    session.commit()

    RetryRecoveryManager().prepare_resume(session, run)

    session.refresh(node)
    session.refresh(run)
    session.refresh(cycle)
    assert node.status == NodeStatus.PENDING.value
    assert node.retry_count == 0
    assert node.error_message is None
    assert run.status == RunStatus.RUNNING.value
    assert cycle.status == CycleStatus.RUNNING.value
