from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import ArtifactRecord
from app.models.schemas import ArtifactManifest, EditOperation


class ArtifactStore:
    RUN_ROOT_PREFIXES = ("workspace/frontend/", "workspace/backend/", "delivery/")

    def __init__(self) -> None:
        self.settings = get_settings()

    def task_root(self, run_id: str) -> Path:
        task_root = self.settings.task_root_dir / run_id
        task_root.mkdir(parents=True, exist_ok=True)
        return task_root

    def cycle_root(self, run_id: str, cycle_index: int) -> Path:
        cycle_dir = self.task_root(run_id) / "cycles" / f"cycle-{cycle_index:02d}"
        cycle_dir.mkdir(parents=True, exist_ok=True)
        return cycle_dir

    def save_artifacts(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str,
        cycle_index: int,
        node_id: str,
        role: str,
        artifacts: list[dict[str, Any]],
    ) -> list[ArtifactManifest]:
        manifests: list[ArtifactManifest] = []
        for artifact in artifacts:
            relative_path = self._safe_relative_path(artifact["name"])
            file_path = self.resolve_output_path(run_id, cycle_index, relative_path.as_posix())
            file_path.parent.mkdir(parents=True, exist_ok=True)
            content = self._serialize_content(artifact.get("content", ""))
            file_path.write_text(content, encoding="utf-8")
            preview = content[:1500]
            record = ArtifactRecord(
                run_id=run_id,
                cycle_id=cycle_id,
                node_id=node_id,
                artifact_type=artifact["artifact_type"],
                name=relative_path.as_posix(),
                path=str(file_path),
                content_type=artifact.get("content_type", "text/markdown"),
                summary=artifact.get("summary", ""),
                artifact_metadata={
                    **artifact.get("metadata", {}),
                    "content_preview": preview,
                    "relative_path": relative_path.as_posix(),
                    "role": role,
                    "path_class": self._path_class(relative_path),
                },
            )
            session.add(record)
            session.flush()
            manifests.append(self._to_manifest(record))
        session.commit()
        return manifests

    def save_role_outputs(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str,
        cycle_index: int,
        node_id: str,
        role: str,
        artifacts: list[dict[str, Any]],
        edit_operations: list[EditOperation],
    ) -> list[ArtifactManifest]:
        saved_artifacts = self.save_artifacts(
            session,
            run_id=run_id,
            cycle_id=cycle_id,
            cycle_index=cycle_index,
            node_id=node_id,
            role=role,
            artifacts=artifacts,
        ) if artifacts else []
        saved_edits = self.apply_edit_operations(
            session,
            run_id=run_id,
            cycle_id=cycle_id,
            cycle_index=cycle_index,
            node_id=node_id,
            role=role,
            operations=edit_operations,
        ) if edit_operations else []
        return [*saved_artifacts, *saved_edits]

    def resolve_output_path(self, run_id: str, cycle_index: int, relative_path: str) -> Path:
        safe_path = self._safe_relative_path(relative_path)
        if safe_path.as_posix().startswith(self.RUN_ROOT_PREFIXES):
            return self.task_root(run_id) / safe_path
        return self.cycle_root(run_id, cycle_index) / safe_path

    def apply_edit_operations(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str,
        cycle_index: int,
        node_id: str,
        role: str,
        operations: list[EditOperation],
    ) -> list[ArtifactManifest]:
        from app.services.workspace_editing import apply_edit_operation

        manifests: list[ArtifactManifest] = []
        for operation in operations:
            relative_path = self._safe_relative_path(operation.path)
            file_path = self.resolve_output_path(run_id, cycle_index, relative_path.as_posix())
            action, preview = apply_edit_operation(file_path, operation)
            record = ArtifactRecord(
                run_id=run_id,
                cycle_id=cycle_id,
                node_id=node_id,
                artifact_type="workspace-edit",
                name=relative_path.as_posix(),
                path=str(file_path),
                content_type="text/plain",
                summary=operation.summary,
                artifact_metadata={
                    "operation": action,
                    "edit_strategy": operation.strategy,
                    "relative_path": relative_path.as_posix(),
                    "role": role,
                    "path_class": self._path_class(relative_path),
                    "content_preview": preview,
                },
            )
            session.add(record)
            session.flush()
            manifests.append(self._to_manifest(record))
        session.commit()
        return manifests

    def list_run_artifacts(self, session: Session, run_id: str) -> list[ArtifactManifest]:
        records = session.scalars(
            select(ArtifactRecord).where(ArtifactRecord.run_id == run_id).order_by(ArtifactRecord.created_at.desc())
        ).all()
        return [self._to_manifest(record) for record in records]

    @staticmethod
    def _to_manifest(record: ArtifactRecord) -> ArtifactManifest:
        data = {
            "id": record.id,
            "run_id": record.run_id,
            "cycle_id": record.cycle_id,
            "node_id": record.node_id,
            "artifact_type": record.artifact_type,
            "name": record.name,
            "path": record.path,
            "content_type": record.content_type,
            "summary": record.summary,
            "metadata": record.artifact_metadata or {},
            "created_at": record.created_at,
        }
        return ArtifactManifest.model_validate(data)

    @staticmethod
    def _serialize_content(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, (dict, list)):
            return json.dumps(content, ensure_ascii=False, indent=2)
        return str(content)

    @classmethod
    def _path_class(cls, relative_path: Path) -> str:
        normalized = relative_path.as_posix()
        if normalized.startswith("workspace/frontend/"):
            return "workspace_frontend"
        if normalized.startswith("workspace/backend/"):
            return "workspace_backend"
        if normalized.startswith("delivery/"):
            return "delivery"
        return "cycle_artifact"

    @staticmethod
    def _safe_relative_path(raw_path: str) -> Path:
        normalized = raw_path.replace("\\", "/").strip().lstrip("/")
        candidate = Path(normalized)
        if not normalized or candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
            raise ValueError(f"Invalid artifact path '{raw_path}'. Artifacts must use safe relative paths.")
        return candidate
