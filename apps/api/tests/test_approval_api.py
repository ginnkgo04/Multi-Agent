from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.routes as routes_module
from app.api.routes import router
from app.db import Base, get_session
from app.models.records import CycleRecord, ProjectRecord, RunRecord


@pytest.fixture
def runtime_spy() -> list[tuple[str, bool, bool]]:
    return []


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, runtime_spy: list[tuple[str, bool, bool]]) -> TestClient:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    state_fixture = {
        "approval_state": "pending",
        "blocked_reason": "waiting_for_plan_approval",
        "last_completed_role": "CA",
    }
    latest_plan = SimpleNamespace(
        id="plan-1",
        summary="CA produced an initial shared implementation plan.",
        approval_state="pending",
        plan_kind="initial",
        plan_payload={
            "execution_contract": {
                "frontend": {
                    "stack_id": "next-fastapi",
                    "required_paths": ["workspace/frontend/app/page.tsx"],
                    "allowed_paths": ["workspace/frontend/"],
                    "constraints": ["Use app router"],
                },
                "backend": {
                    "stack_id": "next-fastapi",
                    "required_paths": ["workspace/backend/app/main.py"],
                    "allowed_paths": ["workspace/backend/"],
                    "constraints": ["Expose read-only public endpoint"],
                },
            },
            "interfaces": [{"name": "GET /api/blossom"}],
            "architecture_decisions": ["Keep the page static and fetch optional blossom metadata."],
            "remediation_plan": {},
        },
    )

    class StubRuntime:
        async def start_run(self, run_id: str, resumed: bool = False, force_restart: bool = False) -> None:
            runtime_spy.append((run_id, resumed, force_restart))

    checkpoint_store = SimpleNamespace(
        latest_for_cycle=lambda session, *, run_id, cycle_id: SimpleNamespace(
            graph_kind="initial",
            serialized_state=state_fixture,
        ),
        save=lambda *args, **kwargs: None,
    )
    context_document_service = SimpleNamespace(get_current_shared_plan=lambda session, run_id: latest_plan)
    memory_service = SimpleNamespace(add_memory=lambda *args, **kwargs: None)
    event_bus = SimpleNamespace(publish=AsyncMock())
    runtime = StubRuntime()
    stub_container = SimpleNamespace(
        checkpoint_store=checkpoint_store,
        context_document_service=context_document_service,
        memory_service=memory_service,
        event_bus=event_bus,
        runtime=runtime,
    )

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    with testing_session_local() as seed_session:
        created_at = datetime.now(timezone.utc)
        seed_session.add(
            ProjectRecord(
                id="project-1",
                name="Demo",
                description="Demo project",
                created_at=created_at,
            )
        )
        seed_session.add(
            RunRecord(
                id="run-1",
                project_id="project-1",
                requirement="Build a sakura landing page",
                status="WAITING_APPROVAL",
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
        seed_session.add(
            CycleRecord(
                id="cycle-1",
                run_id="run-1",
                cycle_index=1,
                status="WAITING_APPROVAL",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        seed_session.commit()

    test_app = FastAPI()
    test_app.include_router(router, prefix="/api")
    test_app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(routes_module, "get_container", lambda: stub_container)

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()


def test_pending_action_returns_approval_context(client: TestClient) -> None:
    response = client.get("/api/runs/run-1/pending-action")

    assert response.status_code == 200
    payload = response.json()
    assert payload["action_type"] == "approval"
    assert payload["approval_context"]["summary"] == "CA produced an initial shared implementation plan."
    assert payload["approval_context"]["execution_contract"]["frontend"]["stack_id"] == "next-fastapi"
    assert payload["approval_context"]["architecture_decisions"] == [
        "Keep the page static and fetch optional blossom metadata."
    ]


def test_approve_accept_resumes_run(
    client: TestClient,
    runtime_spy: list[tuple[str, bool, bool]],
) -> None:
    response = client.post(
        "/api/runs/run-1/approve",
        json={"approved": True, "comment": ""},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "RUNNING"
    assert runtime_spy == [("run-1", True, True)]


def test_approve_reject_moves_run_to_waiting_clarification(
    client: TestClient,
    runtime_spy: list[tuple[str, bool, bool]],
) -> None:
    response = client.post(
        "/api/runs/run-1/approve",
        json={"approved": False, "comment": "The backend contract should be removed."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "WAITING_CLARIFICATION"
    assert runtime_spy == []
