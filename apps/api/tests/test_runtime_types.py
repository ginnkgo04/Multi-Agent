from app.agents.runtime_types import ExecutionBuffer


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
