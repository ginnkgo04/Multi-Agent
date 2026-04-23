import asyncio
from contextlib import suppress
import json
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
from app.api.serializers import to_run_detail
from app.db import Base
from app.db import get_session
from app.models.records import CycleRecord, EventRecord, ProjectRecord, RunRecord
from app.models.schemas import EventMessage, EventType
from app.services.event_bus import EventBus

EVENT_SPECS = [
    (1, EventType.RUN_CREATED),
    (2, EventType.NODE_STARTED),
    (3, EventType.NODE_COMPLETED),
]


def make_session() -> Session:
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
    return testing_session_local()


def seed_run(session: Session) -> RunRecord:
    created_at = datetime.now(timezone.utc)
    session.add(ProjectRecord(id="project-1", name="Demo", description="Demo", created_at=created_at))
    run = RunRecord(
        id="run-1",
        project_id="project-1",
        requirement="Build a sakura landing page",
        status="RUNNING",
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
    session.add(run)
    session.commit()
    return run


def make_event_records(run_id: str, event_specs: list[tuple[int, EventType]] | None = None) -> list[EventRecord]:
    specs = event_specs or EVENT_SPECS
    return [EventRecord(run_id=run_id, sequence=sequence, event_type=event_type.value, payload={}) for sequence, event_type in specs]


def make_event_messages(
    run_id: str,
    cycle_id: str,
    event_specs: list[tuple[int, EventType]] | None = None,
) -> list[EventMessage]:
    specs = event_specs or EVENT_SPECS
    created_at = datetime.now(timezone.utc)
    return [
        EventMessage(
            sequence=sequence,
            type=event_type,
            run_id=run_id,
            cycle_id=cycle_id,
            node_id=None,
            timestamp=created_at,
            payload={},
        )
        for sequence, event_type in specs
    ]


def parse_sse_payloads(body: str) -> list[dict[str, object]]:
    return [json.loads(line.removeprefix("data: ")) for line in body.splitlines() if line.startswith("data: ")]


@pytest.fixture
def api_app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
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

    with testing_session_local() as seed_session:
        created_at = datetime.now(timezone.utc)
        seed_session.add(ProjectRecord(id="project-1", name="Demo", description="Demo", created_at=created_at))
        seed_session.add(
            RunRecord(
                id="run-1",
                project_id="project-1",
                requirement="Build a sakura landing page",
                status="RUNNING",
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
                status="RUNNING",
                created_at=created_at,
                updated_at=created_at,
            )
        )
        seed_session.add_all(make_event_records("run-1"))
        seed_session.commit()

    replay_messages = make_event_messages("run-1", "cycle-1")

    event_bus = SimpleNamespace(
        replay=lambda session, run_id, after_sequence=None: [
            message for message in replay_messages
            if after_sequence is None or message.sequence > after_sequence
        ],
        subscribe=AsyncMock(side_effect=lambda run_id: asyncio.Queue()),
        unsubscribe=AsyncMock(),
    )
    artifact_store = SimpleNamespace(list_run_artifacts=lambda session, run_id: [])
    container = SimpleNamespace(event_bus=event_bus, artifact_store=artifact_store)

    def override_get_session():
        session = testing_session_local()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_session] = override_get_session
    monkeypatch.setattr(routes_module, "SessionLocal", testing_session_local)
    monkeypatch.setattr(routes_module, "get_container", lambda: container)

    return app


@pytest.fixture
def client(api_app: FastAPI) -> TestClient:
    with TestClient(api_app) as test_client:
        yield test_client


def capture_sse_payloads(
    app: FastAPI,
    path: str,
    query_string: bytes = b"",
    expected_payloads: int = 1,
) -> tuple[int, list[dict[str, object]]]:
    async def run_capture() -> tuple[int, list[dict[str, object]]]:
        response_status: int | None = None
        body_chunks: list[bytes] = []
        disconnect_event = asyncio.Event()
        request_sent = False

        async def receive() -> dict[str, object]:
            nonlocal request_sent
            if not request_sent:
                request_sent = True
                return {"type": "http.request", "body": b"", "more_body": False}
            await disconnect_event.wait()
            return {"type": "http.disconnect"}

        async def send(message: dict[str, object]) -> None:
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = int(message["status"])
                return
            if message["type"] != "http.response.body":
                return
            body = message.get("body", b"")
            if body:
                body_chunks.append(body if isinstance(body, bytes) else body.encode())
                if len(parse_sse_payloads(b"".join(body_chunks).decode())) >= expected_payloads:
                    disconnect_event.set()
            if not message.get("more_body", False):
                disconnect_event.set()

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "headers": [(b"accept", b"text/event-stream")],
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "root_path": "",
            "state": {},
            "app": app,
        }

        task = asyncio.create_task(app(scope, receive, send))
        try:
            await asyncio.wait_for(task, timeout=1)
        except asyncio.TimeoutError:
            disconnect_event.set()
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task

        if response_status is None:
            raise AssertionError("No http.response.start message received.")

        payloads = parse_sse_payloads(b"".join(body_chunks).decode())
        return response_status, payloads[:expected_payloads]

    return asyncio.run(run_capture())


def test_to_run_detail_includes_latest_event_sequence() -> None:
    with make_session() as session:
        run = seed_run(session)
        session.add_all(make_event_records(run.id, [(1, EventType.RUN_CREATED), (3, EventType.NODE_COMPLETED)]))
        session.commit()

        detail = to_run_detail(session, run, [])

        assert detail.latest_event_sequence == 3


def test_to_run_detail_uses_zero_when_run_has_no_events() -> None:
    with make_session() as session:
        run = seed_run(session)

        detail = to_run_detail(session, run, [])

        assert detail.latest_event_sequence == 0


def test_event_bus_replay_filters_after_sequence() -> None:
    with make_session() as session:
        run = seed_run(session)
        session.add_all(make_event_records(run.id))
        session.commit()

        replay = EventBus().replay(session, run.id, after_sequence=2)

        assert [message.sequence for message in replay] == [3]


def test_get_run_includes_latest_event_sequence(client: TestClient) -> None:
    response = client.get("/api/runs/run-1")

    assert response.status_code == 200
    assert response.json()["latest_event_sequence"] == 3


def test_stream_run_events_replays_all_events_without_cursor(api_app: FastAPI) -> None:
    status_code, payloads = capture_sse_payloads(api_app, "/api/runs/run-1/events/stream", expected_payloads=3)

    assert status_code == 200
    assert [payload["sequence"] for payload in payloads] == [1, 2, 3]
    assert [payload["type"] for payload in payloads] == ["run_created", "node_started", "node_completed"]


def test_stream_run_events_filters_replay_by_after_sequence(api_app: FastAPI) -> None:
    status_code, payloads = capture_sse_payloads(
        api_app,
        "/api/runs/run-1/events/stream",
        query_string=b"after_sequence=2",
        expected_payloads=1,
    )

    assert status_code == 200
    assert len(payloads) == 1
    assert payloads[0]["sequence"] == 3
    assert payloads[0]["type"] == "node_completed"
    assert payloads[0]["run_id"] == "run-1"
    assert payloads[0]["cycle_id"] == "cycle-1"
