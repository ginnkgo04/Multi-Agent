from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models.schemas import EditOperation
from app.services.artifact_store import ArtifactStore


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    local_session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    return local_session()


def test_safe_relative_path_allows_nested_task_files() -> None:
    path = ArtifactStore._safe_relative_path("workspace/frontend/app/page.tsx")

    assert path.as_posix() == "workspace/frontend/app/page.tsx"


def test_safe_relative_path_rejects_parent_escape() -> None:
    with pytest.raises(ValueError):
        ArtifactStore._safe_relative_path("../outside.txt")


def test_resolve_output_path_routes_workspace_and_delivery_to_run_root(tmp_path: Path) -> None:
    store = ArtifactStore()
    store.settings.task_root_dir = tmp_path

    workspace_path = store.resolve_output_path("run-1", 2, "workspace/frontend/app/page.tsx")
    delivery_path = store.resolve_output_path("run-1", 2, "delivery/runbook.md")
    quality_path = store.resolve_output_path("run-1", 2, "quality/report.md")

    assert workspace_path == tmp_path / "run-1" / "workspace" / "frontend" / "app" / "page.tsx"
    assert delivery_path == tmp_path / "run-1" / "delivery" / "runbook.md"
    assert quality_path == tmp_path / "run-1" / "cycles" / "cycle-02" / "quality" / "report.md"


def test_apply_edit_operations_updates_existing_workspace_file_in_place(tmp_path: Path) -> None:
    session = make_session()
    store = ArtifactStore()
    store.settings.task_root_dir = tmp_path
    target = tmp_path / "run-1" / "workspace" / "frontend" / "app" / "page.tsx"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("export default function Page() { return <main>Polar Bear</main>; }\n", encoding="utf-8")

    manifests = store.apply_edit_operations(
        session,
        run_id="run-1",
        cycle_id="cycle-2",
        cycle_index=2,
        node_id="node-fd",
        role="FD",
        operations=[
            EditOperation(
                path="workspace/frontend/app/page.tsx",
                operation="update",
                strategy="replace",
                summary="Swap the featured animal",
                old_text="Polar Bear",
                new_text="Arctic Fox",
            )
        ],
    )

    assert "Arctic Fox" in target.read_text(encoding="utf-8")
    assert manifests[0].metadata["operation"] == "update"


def test_apply_edit_operations_deletes_explicit_workspace_file(tmp_path: Path) -> None:
    session = make_session()
    store = ArtifactStore()
    store.settings.task_root_dir = tmp_path
    target = tmp_path / "run-1" / "workspace" / "frontend" / "components" / "LegacyBanner.tsx"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("export function LegacyBanner() { return null; }\n", encoding="utf-8")

    store.apply_edit_operations(
        session,
        run_id="run-1",
        cycle_id="cycle-2",
        cycle_index=2,
        node_id="node-fd",
        role="FD",
        operations=[
            EditOperation(
                path="workspace/frontend/components/LegacyBanner.tsx",
                operation="delete",
                strategy="delete",
                summary="Remove the deprecated banner",
            )
        ],
    )

    assert target.exists() is False


def test_apply_edit_operations_rejects_whole_file_rewrite_for_existing_file(tmp_path: Path) -> None:
    session = make_session()
    store = ArtifactStore()
    store.settings.task_root_dir = tmp_path
    target = tmp_path / "run-1" / "workspace" / "backend" / "app" / "services.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    original = "def current_service():\n    return 'polar-bear'\n"
    target.write_text(original, encoding="utf-8")

    with pytest.raises(ValueError, match="whole-file rewrite"):
        store.apply_edit_operations(
            session,
            run_id="run-1",
            cycle_id="cycle-2",
            cycle_index=2,
            node_id="node-bd",
            role="BD",
            operations=[
                EditOperation(
                    path="workspace/backend/app/services.py",
                    operation="update",
                    strategy="replace",
                    summary="Attempt to replace the full file body",
                    old_text=original,
                    new_text="def replacement():\n    return 'arctic-fox'\n",
                )
            ],
        )
