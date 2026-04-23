from pathlib import Path

import pytest
from pydantic import ValidationError

from app.agents.runtime_types import ExecutionBuffer
from app.models.schemas import EditOperation, WorkspaceFileSnapshot


def test_execution_buffer_tracks_artifacts_and_submission() -> None:
    buffer = ExecutionBuffer()

    buffer.emit_artifact(
        path="workspace/frontend/app/page.tsx",
        artifact_type="source-code",
        content_type="text/x.typescript",
        summary="Main page",
        content="export default function Page() { return null; }",
        metadata={"role": "FD"},
    )
    buffer.submit(
        summary="Frontend scaffold emitted.",
        handoff_notes="Backend can integrate with the generated route.",
        result_payload={"implemented_features": ["landing page"]},
        confidence=0.81,
    )

    assert buffer.submitted is True
    assert len(buffer.artifacts) == 1
    assert buffer.artifacts[0]["name"] == "workspace/frontend/app/page.tsx"
    assert buffer.result_payload["implemented_features"] == ["landing page"]


def test_workspace_file_snapshot_captures_existing_file_content(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("workspace content", encoding="utf-8")

    snapshot = WorkspaceFileSnapshot(
        path="workspace/notes.txt",
        content=file_path.read_text(encoding="utf-8"),
        exists=file_path.exists(),
        size_bytes=file_path.stat().st_size,
    )

    assert snapshot.path == "workspace/notes.txt"
    assert snapshot.content == "workspace content"
    assert snapshot.exists is True
    assert snapshot.size_bytes == len("workspace content")


def test_execution_buffer_tracks_workspace_edit_operations() -> None:
    buffer = ExecutionBuffer()
    operation = EditOperation(
        path="workspace/frontend/app/page.tsx",
        operation="update",
        strategy="patch",
        summary="Add workspace editing schemas.",
        unified_diff="@@ -1 +1 @@",
    )

    buffer.emit_edit_operation(operation)

    assert len(buffer.edit_operations) == 1
    buffered_operation = buffer.edit_operations[0]
    assert buffered_operation["path"] == "workspace/frontend/app/page.tsx"
    assert buffered_operation["operation"] == "update"
    assert buffered_operation["strategy"] == "patch"
    assert buffered_operation["unified_diff"] == "@@ -1 +1 @@"


@pytest.mark.parametrize(
    ("payload", "error_fragment"),
    [
        (
            {
                "path": "new.txt",
                "operation": "create",
                "strategy": "replace",
                "content": "hello",
            },
            "create operations require strategy='create'",
        ),
        (
            {
                "path": "new.txt",
                "operation": "create",
                "strategy": "create",
            },
            "create operations require non-empty content",
        ),
        (
            {
                "path": "old.txt",
                "operation": "delete",
                "strategy": "patch",
            },
            "delete operations require strategy='delete'",
        ),
        (
            {
                "path": "file.txt",
                "operation": "update",
                "strategy": "replace",
                "new_text": "next",
            },
            "replace updates require both old_text and new_text",
        ),
        (
            {
                "path": "file.txt",
                "operation": "update",
                "strategy": "patch",
            },
            "patch updates require unified_diff",
        ),
        (
            {
                "path": "file.txt",
                "operation": "update",
                "strategy": "insert_before",
                "new_text": "",
                "anchors": [],
            },
            "insert updates require at least one anchor and non-empty new_text",
        ),
    ],
)
def test_edit_operation_rejects_invalid_strategy_payload_combinations(
    payload: dict[str, str | list[str]],
    error_fragment: str,
) -> None:
    with pytest.raises(ValidationError, match=error_fragment):
        EditOperation(**payload)
