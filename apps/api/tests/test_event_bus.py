from datetime import datetime, timezone

from app.models.schemas import EventMessage, EventType
from app.services.event_bus import EventBus


def test_runtime_log_is_written_to_task_workspace(tmp_path) -> None:
    bus = EventBus()
    bus.settings.task_root_dir = tmp_path
    message = EventMessage(
        sequence=1,
        type=EventType.RUN_CREATED,
        run_id="run-123",
        cycle_id=None,
        node_id=None,
        timestamp=datetime.now(timezone.utc),
        payload={"hello": "world"},
    )

    bus._append_runtime_log(message)

    log_path = tmp_path / "run-123" / "logs" / "runtime.log"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert '"type": "run_created"' in content
    assert '"hello": "world"' in content
