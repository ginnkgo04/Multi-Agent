from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.records import ArtifactRecord, CycleRecord, MemoryRecord, MemorySummaryRecord, ProjectRecord, RunRecord, SharedPlanRecord, UserPreferenceRecord


class MemoryService:
    def add_memory(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str | None,
        memory_type: str,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        session.add(
            MemoryRecord(
                run_id=run_id,
                cycle_id=cycle_id,
                memory_type=memory_type,
                content=content,
                memory_metadata=metadata or {},
            )
        )
        session.commit()

    def list_recent(self, session: Session, run_id: str, limit: int = 6) -> list[str]:
        records = self.list_recent_records(session, run_id, limit=limit)
        return [record.content for record in reversed(records)]

    def list_recent_records(self, session: Session, run_id: str, limit: int = 6) -> list[MemoryRecord]:
        return list(session.scalars(
            select(MemoryRecord).where(MemoryRecord.run_id == run_id).order_by(desc(MemoryRecord.created_at)).limit(limit)
        ).all())

    def summarize_cycles(self, session: Session, run_id: str) -> list[str]:
        records = self.list_summaries(session, run_id, summary_type="cycle_summary")
        return [record.content for record in records]

    def create_summary(
        self,
        session: Session,
        *,
        run_id: str,
        project_id: str | None,
        cycle_id: str,
        summary_type: str,
        content: str,
        metadata: dict | None = None,
    ) -> MemorySummaryRecord:
        record = MemorySummaryRecord(
            run_id=run_id,
            project_id=project_id,
            cycle_id=cycle_id,
            summary_type=summary_type,
            content=content,
            summary_metadata=metadata or {},
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def list_summaries(self, session: Session, run_id: str, summary_type: str | None = None) -> list[MemorySummaryRecord]:
        query = select(MemorySummaryRecord).where(MemorySummaryRecord.run_id == run_id).order_by(MemorySummaryRecord.created_at)
        if summary_type:
            query = query.where(MemorySummaryRecord.summary_type == summary_type)
        return list(session.scalars(query).all())

    def list_project_template_profiles(self, session: Session, project_id: str) -> list[MemorySummaryRecord]:
        return list(session.scalars(
            select(MemorySummaryRecord)
            .where(
                MemorySummaryRecord.project_id == project_id,
                MemorySummaryRecord.summary_type == "project_template_profile",
            )
            .order_by(MemorySummaryRecord.created_at.desc())
        ).all())

    def get_current_project_template_profile(self, session: Session, project_id: str) -> MemorySummaryRecord | None:
        for record in self.list_project_template_profiles(session, project_id):
            if (record.summary_metadata or {}).get("is_current"):
                return record
        return None

    def resolve_effective_template_context(
        self,
        session: Session,
        *,
        project_id: str,
        requested_template_context: dict | None,
    ) -> tuple[dict, str, MemorySummaryRecord | None]:
        normalized = dict(requested_template_context or {})
        if normalized:
            return normalized, "explicit", None
        preference_context = self.resolve_preference_context(session, project_id)
        profile = self.get_current_project_template_profile(session, project_id)
        if profile:
            inherited = profile.summary_metadata.get("template_context")
            if isinstance(inherited, dict) and inherited:
                return {**dict(inherited), **preference_context}, "project_profile", profile
        if preference_context:
            return preference_context, "user_preference", profile
        return {}, "empty", profile

    def list_active_preferences(self, session: Session, project_id: str) -> list[UserPreferenceRecord]:
        return list(session.scalars(
            select(UserPreferenceRecord)
            .where(UserPreferenceRecord.project_id == project_id, UserPreferenceRecord.is_active == True)  # noqa: E712
            .order_by(UserPreferenceRecord.created_at)
        ).all())

    def resolve_preference_context(self, session: Session, project_id: str) -> dict:
        context: dict[str, str] = {}
        for record in self.list_active_preferences(session, project_id):
            context[record.preference_key] = record.value
        return context

    def upsert_user_preferences(
        self,
        session: Session,
        *,
        project_id: str,
        preferences: dict | None,
        source: str = "explicit",
        applies_to: str = "global",
    ) -> list[UserPreferenceRecord]:
        if not isinstance(preferences, dict):
            return []
        records: list[UserPreferenceRecord] = []
        for raw_key, raw_value in preferences.items():
            key = str(raw_key).strip()
            value = str(raw_value).strip()
            if not key or not value:
                continue
            record = session.scalar(
                select(UserPreferenceRecord).where(
                    UserPreferenceRecord.project_id == project_id,
                    UserPreferenceRecord.preference_key == key,
                    UserPreferenceRecord.is_active == True,  # noqa: E712
                )
            )
            if record is None:
                record = UserPreferenceRecord(
                    project_id=project_id,
                    preference_key=key,
                    value=value,
                    source=source,
                    applies_to=applies_to,
                    confidence=100 if source == "explicit" else 80,
                )
                session.add(record)
            else:
                record.value = value
                record.source = source
                record.applies_to = applies_to
                record.confidence = 100 if source == "explicit" else 80
                record.last_confirmed_at = datetime.now(timezone.utc)
            records.append(record)
        session.commit()
        return records

    def build_cycle_summary(
        self,
        session: Session,
        *,
        run_id: str,
        cycle_id: str,
        cycle_index: int,
        qt_payload: dict,
    ) -> tuple[str, dict]:
        cycle_memories = session.scalars(
            select(MemoryRecord).where(MemoryRecord.run_id == run_id, MemoryRecord.cycle_id == cycle_id).order_by(MemoryRecord.created_at)
        ).all()
        status = str(qt_payload.get("status", "UNKNOWN")).upper()
        remediation = str(qt_payload.get("remediation_requirement", "none"))
        summary_lines = [
            f"Cycle {cycle_index} status: {status}",
            f"Remediation: {remediation}",
        ]
        for record in cycle_memories[-6:]:
            role = str((record.memory_metadata or {}).get("role", record.memory_type)).upper()
            summary_lines.append(f"{role}: {record.content}")
        metadata = {
            "cycle_index": cycle_index,
            "status": status,
            "memory_count": len(cycle_memories),
        }
        return "\n".join(summary_lines), metadata

    def build_project_template_profile(
        self,
        session: Session,
        *,
        project_id: str,
        run: RunRecord,
        cycle_id: str,
    ) -> tuple[str, dict]:
        project = session.get(ProjectRecord, project_id)
        shared_plan = session.scalar(
            select(SharedPlanRecord).where(SharedPlanRecord.run_id == run.id, SharedPlanRecord.is_current == True).order_by(desc(SharedPlanRecord.created_at))  # noqa: E712
        )
        artifacts = session.scalars(
            select(ArtifactRecord).where(ArtifactRecord.run_id == run.id).order_by(ArtifactRecord.created_at.desc())
        ).all()
        artifact_roots = sorted({record.name.split("/", 1)[0] for record in artifacts if record.name})
        template_context = dict(run.template_context or {})
        template_context["project_template"] = project.template if project else template_context.get("project_template", "default-template")
        template_context["preferred_artifact_roots"] = artifact_roots
        if shared_plan and shared_plan.summary:
            template_context["shared_plan_summary"] = shared_plan.summary
        if shared_plan:
            plan_payload = shared_plan.plan_payload or {}
            if isinstance(plan_payload.get("interfaces"), list):
                template_context["interface_highlights"] = plan_payload["interfaces"][:4]
            if isinstance(plan_payload.get("architecture_decisions"), list):
                template_context["architecture_decisions"] = plan_payload["architecture_decisions"][:4]
        content_lines = [
            f"Project template: {template_context['project_template']}",
            f"Source run: {run.id}",
            f"Stable artifact roots: {', '.join(artifact_roots) if artifact_roots else 'none'}",
        ]
        if shared_plan and shared_plan.summary:
            content_lines.append(f"Shared plan summary: {shared_plan.summary}")
        if run.template_context:
            content_lines.append("Base template context:")
            content_lines.append(json.dumps(run.template_context, ensure_ascii=False, indent=2))
        metadata = {
            "source_run_id": run.id,
            "source_cycle_id": cycle_id,
            "template_context": template_context,
        }
        return "\n".join(content_lines), metadata

    def upsert_project_template_profile(
        self,
        session: Session,
        *,
        project_id: str,
        run: RunRecord,
        cycle_id: str,
    ) -> MemorySummaryRecord:
        existing_profiles = self.list_project_template_profiles(session, project_id)
        next_version = len(existing_profiles) + 1
        for record in existing_profiles:
            metadata = dict(record.summary_metadata or {})
            if metadata.get("is_current"):
                metadata["is_current"] = False
                record.summary_metadata = metadata
        content, metadata = self.build_project_template_profile(session, project_id=project_id, run=run, cycle_id=cycle_id)
        metadata = {
            **metadata,
            "version_index": next_version,
            "is_current": True,
        }
        session.commit()
        return self.create_summary(
            session,
            run_id=run.id,
            project_id=project_id,
            cycle_id=cycle_id,
            summary_type="project_template_profile",
            content=content,
            metadata=metadata,
        )

    def backfill_project_ids(self, session: Session) -> None:
        records = session.scalars(select(MemorySummaryRecord).where(MemorySummaryRecord.project_id.is_(None))).all()
        changed = False
        for record in records:
            run = session.get(RunRecord, record.run_id)
            if run is None:
                continue
            record.project_id = run.project_id
            changed = True
        if changed:
            session.commit()
