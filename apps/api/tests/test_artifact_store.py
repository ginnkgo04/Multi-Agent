import pytest

from app.services.artifact_store import ArtifactStore


def test_safe_relative_path_allows_nested_task_files() -> None:
    path = ArtifactStore._safe_relative_path("workspace/frontend/app/page.tsx")

    assert path.as_posix() == "workspace/frontend/app/page.tsx"


def test_safe_relative_path_rejects_parent_escape() -> None:
    with pytest.raises(ValueError):
        ArtifactStore._safe_relative_path("../outside.txt")
