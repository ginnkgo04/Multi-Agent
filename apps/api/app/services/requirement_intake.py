from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.records import CycleRecord, ProjectRecord, RunRecord
from app.models.schemas import CycleStatus, ProjectCreate, ProjectRead, RunRequest, RunStatus
from app.services.memory_service import MemoryService


class RequirementIntakeService:
    def __init__(self, memory_service: MemoryService | None = None) -> None:
        self.settings = get_settings()
        self.memory_service = memory_service or MemoryService()

    def create_project(self, session: Session, payload: ProjectCreate) -> ProjectRead:
        record = ProjectRecord(name=payload.name, description=payload.description, template=payload.template)
        session.add(record)
        session.commit()
        session.refresh(record)
        return ProjectRead.model_validate(record, from_attributes=True)

    def create_run(self, session: Session, payload: RunRequest, provider_name: str, embedding_provider_name: str) -> RunRecord:
        max_cycles = payload.max_cycles or self.settings.max_cycles
        project = session.get(ProjectRecord, payload.project_id)
        effective_template_context, template_context_origin, profile = self.memory_service.resolve_effective_template_context(
            session,
            project_id=payload.project_id,
            requested_template_context=payload.template_context,
        )
        run = RunRecord(
            project_id=payload.project_id,
            requirement=payload.requirement,
            status=RunStatus.PENDING.value,
            current_cycle=1,
            max_cycles=max_cycles,
            provider_name=provider_name,
            embedding_provider_name=embedding_provider_name,
            manual_approval=payload.manual_approval,
            template_context=effective_template_context,
            template_context_origin=template_context_origin,
        )
        session.add(run)
        session.flush()
        self._initialize_task_workspace(
            run_id=run.id,
            project_name=project.name if project else payload.project_id,
            payload=payload,
            provider_name=provider_name,
            embedding_provider_name=embedding_provider_name,
            max_cycles=max_cycles,
            effective_template_context=effective_template_context,
            template_context_origin=template_context_origin,
            inherited_profile_id=profile.id if profile else None,
        )
        cycle = CycleRecord(run_id=run.id, cycle_index=1, status=CycleStatus.PENDING.value)
        session.add(cycle)
        session.commit()
        session.refresh(run)
        return run

    def _initialize_task_workspace(
        self,
        *,
        run_id: str,
        project_name: str,
        payload: RunRequest,
        provider_name: str,
        embedding_provider_name: str,
        max_cycles: int,
        effective_template_context: dict,
        template_context_origin: str,
        inherited_profile_id: str | None,
    ) -> None:
        task_root = self.settings.task_root_dir / run_id
        input_dir = task_root / "input"
        logs_dir = task_root / "logs"
        input_dir.mkdir(parents=True, exist_ok=True)
        logs_dir.mkdir(parents=True, exist_ok=True)

        (input_dir / "requirement.md").write_text(
            "# Requirement\n\n"
            f"Project: {project_name}\n\n"
            f"{payload.requirement.strip()}\n",
            encoding="utf-8",
        )
        (input_dir / "run_request.json").write_text(
            json.dumps(
                {
                    "run_id": run_id,
                    "project_id": payload.project_id,
                    "project_name": project_name,
                    "requirement": payload.requirement,
                    "provider_name": provider_name,
                    "embedding_provider_name": embedding_provider_name,
                    "manual_approval": payload.manual_approval,
                    "template_context": effective_template_context,
                    "template_context_origin": template_context_origin,
                    "inherited_template_profile_id": inherited_profile_id,
                    "max_cycles": max_cycles,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (task_root / "README.md").write_text(
            "# Task Workspace\n\n"
            "This directory contains the live outputs for one orchestration run.\n\n"
            "## Layout\n\n"
            "- `input/`: original requirement and run request metadata\n"
            "- `logs/runtime.log`: append-only runtime event log for this run\n"
            "- `cycles/cycle-xx/requirements`: PC outputs\n"
            "- `cycles/cycle-xx/architecture`: CA outputs\n"
            "- `cycles/cycle-xx/workspace/frontend`: FD generated frontend code\n"
            "- `cycles/cycle-xx/workspace/backend`: BD generated backend code\n"
            "- `cycles/cycle-xx/delivery`: DE delivery bundle\n"
            "- `cycles/cycle-xx/quality`: QT reports and remediation notes\n",
            encoding="utf-8",
        )
