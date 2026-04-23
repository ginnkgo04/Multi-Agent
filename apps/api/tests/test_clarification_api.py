from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

import app.api.routes as routes_module
from app.api.clarification import build_clarification_context, normalize_clarification_message
from app.api.routes import router
from app.db import Base, get_session
from app.models.records import CycleRecord, NodeExecutionRecord, ProjectRecord, RunRecord


def test_build_clarification_context_reads_pc_checkpoint_payload() -> None:
    state = {
        "node_outputs": {
            "PC": {
                "requirement_brief": "Build a sakura landing page",
                "intent": {
                    "clarifying_questions": ["Who is the page for?"],
                },
                "requirement_fidelity": {
                    "assumed_defaults": ["Static single-page site"],
                },
                "acceptance_criteria": {"must_have": ["hero"]},
                "work_breakdown": ["clarify scope", "draft UI"],
            }
        },
        "clarification_history": [{"message": "Use Chinese copy", "target_role": "PC"}],
    }

    context = build_clarification_context(state)

    assert context.requirement_brief == "Build a sakura landing page"
    assert context.clarifying_questions == ["Who is the page for?"]
    assert context.assumed_defaults == ["Static single-page site"]
    assert context.acceptance_criteria["must_have"] == ["hero"]
    assert context.clarification_history[0]["message"] == "Use Chinese copy"


def test_normalize_clarification_message_requires_feedback_for_reject_defaults() -> None:
    try:
        normalize_clarification_message("reject_defaults", "   ")
    except ValueError as exc:
        assert "requires feedback" in str(exc)
    else:  # pragma: no cover - regression guard
        raise AssertionError("Expected reject_defaults to require feedback.")


def test_normalize_clarification_message_generates_accept_message() -> None:
    message = normalize_clarification_message("accept_defaults", "")

    assert message == "User accepted the current default assumptions and requested execution to continue."


@pytest.fixture
def runtime_spy() -> list[tuple[str, bool, bool]]:
    return []


@pytest.fixture
def checkpoint_spy() -> list[dict]:
    return []


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    runtime_spy: list[tuple[str, bool, bool]],
    checkpoint_spy: list[dict],
) -> TestClient:
    engine = create_engine(
        "sqlite://",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    state_fixture = {
        "clarification_target_role": "PC",
        "blocked_reason": "waiting_for_requirement_clarification",
        "clarification_history": [{"message": "Use Chinese copy", "target_role": "PC"}],
        "node_outputs": {
            "PC": {
                "requirement_brief": "Build a sakura landing page",
                "intent": {"needs_clarification": True, "clarifying_questions": ["Who is the page for?"]},
                "requirement_fidelity": {
                    "assumed_defaults": ["Static single-page site"],
                    "semantic_coverage_score": 0.7,
                    "constraint_retention_score": 0.8,
                    "clarification_needed": True,
                },
                "acceptance_criteria": {"must_have": ["hero"]},
                "work_breakdown": ["clarify scope", "draft UI"],
            }
        },
    }

    class StubRuntime:
        async def start_run(self, run_id: str, resumed: bool = False, force_restart: bool = False) -> None:
            runtime_spy.append((run_id, resumed, force_restart))

    checkpoint_store = SimpleNamespace(
        latest_for_cycle=lambda session, *, run_id, cycle_id: SimpleNamespace(
            graph_kind="initial",
            serialized_state=state_fixture,
        ),
        save=lambda *args, **kwargs: checkpoint_spy.append(kwargs) or None,
    )
    context_document_service = SimpleNamespace(get_current_shared_plan=lambda session, run_id: None)
    memory_service = SimpleNamespace(
        add_memory=lambda *args, **kwargs: None,
        upsert_user_preferences=lambda *args, **kwargs: None,
    )
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
                status="WAITING_CLARIFICATION",
                current_cycle=1,
                max_cycles=3,
                provider_name="primary-llm",
                embedding_provider_name="primary-embedding",
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
                status="WAITING_CLARIFICATION",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        seed_session.add(
            NodeExecutionRecord(
                id="node-pc",
                run_id="run-1",
                cycle_id="cycle-1",
                role="PC",
                batch_index=0,
                status="COMPLETED",
                retry_count=0,
                task_spec={},
                result_payload=state_fixture["node_outputs"]["PC"],
            )
        )
        seed_session.add(
            NodeExecutionRecord(
                id="node-ca",
                run_id="run-1",
                cycle_id="cycle-1",
                role="CA",
                batch_index=1,
                status="PENDING",
                retry_count=0,
                task_spec={},
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


def test_pending_action_returns_clarification_context(client: TestClient) -> None:
    response = client.get("/api/runs/run-1/pending-action")

    assert response.status_code == 200
    payload = response.json()
    assert payload["action_type"] == "clarification"
    assert payload["clarification_context"]["clarifying_questions"] == ["Who is the page for?"]


def test_clarify_accept_defaults_resumes_without_message(
    client: TestClient,
    runtime_spy: list[tuple[str, bool, bool]],
    checkpoint_spy: list[dict],
) -> None:
    response = client.post(
        "/api/runs/run-1/clarify",
        json={"decision": "accept_defaults", "message": "", "structured_context": {}},
    )

    assert response.status_code == 200
    assert runtime_spy == [("run-1", True, True)]
    saved_state = checkpoint_spy[-1]["serialized_state"]
    assert saved_state["last_completed_role"] == "PC"
    assert saved_state["node_outputs"]["PC"]["intent"]["needs_clarification"] is False
    assert saved_state["node_outputs"]["PC"]["intent"]["clarifying_questions"] == []
    assert saved_state["node_outputs"]["PC"]["requirement_fidelity"]["clarification_needed"] is False
    assert saved_state["node_outputs"]["PC"]["requirement_fidelity"]["semantic_coverage_score"] >= 0.85
    assert saved_state["node_outputs"]["PC"]["requirement_fidelity"]["constraint_retention_score"] >= 0.90
    assert saved_state["clarification_accepted_target_role"] == "PC"


def test_clarify_reject_defaults_requires_message(client: TestClient) -> None:
    response = client.post(
        "/api/runs/run-1/clarify",
        json={"decision": "reject_defaults", "message": "   ", "structured_context": {}},
    )

    assert response.status_code == 400
    assert "requires feedback" in response.text
