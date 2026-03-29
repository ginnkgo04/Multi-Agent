from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.records import ArtifactRecord, CycleRecord, MemorySummaryRecord, NodeExecutionRecord, RunRecord
from app.models.schemas import AgentTaskContext, ArtifactManifest, ContextSource, ContextSourceType, ProviderConfig, Role
from app.services.artifact_store import ArtifactStore
from app.services.context_budgeter import ContextBudgeter
from app.services.context_document_service import ContextDocumentService
from app.services.memory_service import MemoryService
from app.services.workflow_graph_builder import role_dependencies_for_cycle


class ContextAssembler:
    def __init__(
        self,
        artifact_store: ArtifactStore,
        memory_service: MemoryService,
        context_documents: ContextDocumentService,
        budgeter: ContextBudgeter,
    ) -> None:
        self.artifact_store = artifact_store
        self.memory_service = memory_service
        self.context_documents = context_documents
        self.budgeter = budgeter

    async def build_context(
        self,
        session: Session,
        *,
        run: RunRecord,
        cycle: CycleRecord,
        node: NodeExecutionRecord,
        chat_config: ProviderConfig,
        embedding_provider,
    ) -> AgentTaskContext:
        upstream_artifacts = self._artifact_manifests(session, cycle, node)
        shared_plan_record = self.context_documents.get_current_shared_plan(session, run.id)
        project_profile = self.memory_service.get_current_project_template_profile(session, run.project_id)
        retrieved_context = await self.context_documents.retrieve(
            session,
            run.project_id,
            query=f"{run.requirement}\n{cycle.remediation_requirement or ''}\n{node.role}",
            embedding_provider=embedding_provider,
            run_id=run.id,
            source_types=[ContextSourceType.KNOWLEDGE.value, ContextSourceType.ARTIFACT.value],
        )
        cycle_summaries = self.memory_service.list_summaries(session, run.id, summary_type="cycle_summary")
        recent_memories = self.memory_service.list_recent_records(session, run.id)

        context_sources = self._build_context_sources(
            run=run,
            shared_plan_record=shared_plan_record,
            project_profile=project_profile,
            upstream_artifacts=upstream_artifacts,
            retrieved_context=retrieved_context,
            cycle_summaries=cycle_summaries,
            recent_memories=recent_memories,
        )
        budgeted_sources, budget_metadata = self.budgeter.apply([source.model_dump(mode="python") for source in context_sources])
        ordered_sources = [ContextSource.model_validate(source) for source in budgeted_sources]
        task_spec = dict(node.task_spec or {})
        shared_plan = dict(shared_plan_record.plan_payload or {}) if shared_plan_record else {}
        included_sources = [source for source in ordered_sources if source.included]
        return AgentTaskContext(
            role=Role(node.role),
            project_id=run.project_id,
            run_id=run.id,
            cycle_id=cycle.id,
            cycle_index=cycle.cycle_index,
            task_spec=task_spec,
            shared_plan=shared_plan,
            shared_plan_id=shared_plan_record.id if shared_plan_record else None,
            upstream_artifacts=self._budgeted_upstream_artifacts(upstream_artifacts, ordered_sources),
            retrieved_context=self._included_retrieved_docs(ordered_sources),
            provider_config=chat_config,
            memories=self._included_memories(ordered_sources),
            original_requirement=run.requirement,
            template_context=run.template_context or {},
            template_context_origin=run.template_context_origin,
            context_sources=included_sources,
            context_metadata={
                **budget_metadata,
                "template_context_origin": run.template_context_origin,
            },
        )

    def _build_context_sources(
        self,
        *,
        run: RunRecord,
        shared_plan_record,
        project_profile,
        upstream_artifacts: list[ArtifactManifest],
        retrieved_context: list[dict],
        cycle_summaries: list[MemorySummaryRecord],
        recent_memories: list,
    ) -> list[ContextSource]:
        sources: list[ContextSource] = [
            ContextSource(
                source_type=ContextSourceType.REQUIREMENT,
                source_id=run.id,
                path=f"runs/{run.id}/requirement",
                excerpt=run.requirement,
                metadata={"scope": "run"},
                scope="run",
                section="requirement",
                order_index=0,
            )
        ]
        if shared_plan_record is not None:
            sources.append(
                ContextSource(
                    source_type=ContextSourceType.SHARED_PLAN,
                    source_id=shared_plan_record.id,
                    path=f"runs/{run.id}/shared-plans/{shared_plan_record.id}",
                    excerpt=shared_plan_record.summary or str(shared_plan_record.plan_payload),
                    metadata={
                        "scope": "run",
                        "version_index": shared_plan_record.version_index,
                    },
                    scope="run",
                    section="shared_plan",
                    order_index=len(sources),
                )
            )
        if project_profile is not None:
            sources.append(
                ContextSource(
                    source_type=ContextSourceType.MEMORY,
                    source_id=project_profile.id,
                    path=f"projects/{run.project_id}/template-profile/{project_profile.id}",
                    excerpt=project_profile.content,
                    metadata={
                        **(project_profile.summary_metadata or {}),
                        "scope": "project",
                        "summary_type": project_profile.summary_type,
                    },
                    scope="project",
                    section="project_template_profile",
                    order_index=len(sources),
                )
            )
        for artifact in upstream_artifacts:
            sources.append(
                ContextSource(
                    source_type=ContextSourceType.ARTIFACT,
                    source_id=artifact.id,
                    path=artifact.path,
                    excerpt=str((artifact.metadata or {}).get("content_preview", ""))[:900],
                    metadata={
                        **(artifact.metadata or {}),
                        "scope": "run",
                    },
                    scope="run",
                    section="upstream_artifacts",
                    order_index=len(sources),
                )
            )
        for item in retrieved_context:
            sources.append(
                ContextSource(
                    source_type=ContextSourceType(item["source_type"]),
                    source_id=item.get("source_id"),
                    path=item.get("path"),
                    excerpt=item.get("excerpt", item.get("content", "")),
                    metadata=item.get("metadata", {}),
                    score=item.get("score"),
                    scope=item.get("scope"),
                    section="retrieved_docs",
                    order_index=len(sources),
                )
            )
        for record in cycle_summaries:
            sources.append(
                ContextSource(
                    source_type=ContextSourceType.MEMORY,
                    source_id=record.id,
                    path=f"runs/{run.id}/memory-summaries/{record.id}",
                    excerpt=record.content,
                    metadata={
                        **(record.summary_metadata or {}),
                        "scope": "run",
                        "summary_type": record.summary_type,
                    },
                    scope="run",
                    section="cycle_summaries",
                    order_index=len(sources),
                )
            )
        for record in recent_memories:
            sources.append(
                ContextSource(
                    source_type=ContextSourceType.MEMORY,
                    source_id=record.id,
                    path=f"runs/{run.id}/memories/{record.id}",
                    excerpt=record.content,
                    metadata={
                        **(record.memory_metadata or {}),
                        "scope": "run",
                        "memory_type": record.memory_type,
                    },
                    scope="run",
                    section="recent_memories",
                    order_index=len(sources),
                )
            )
        return sources

    def _artifact_manifests(self, session: Session, cycle: CycleRecord, node: NodeExecutionRecord) -> list[ArtifactManifest]:
        upstream_roles = role_dependencies_for_cycle(cycle.cycle_index)[Role(node.role)]
        upstream_nodes = session.scalars(
            select(NodeExecutionRecord).where(
                NodeExecutionRecord.cycle_id == cycle.id,
                NodeExecutionRecord.role.in_([role.value for role in upstream_roles]),
            )
        ).all()
        upstream_ids = [upstream.id for upstream in upstream_nodes]
        if not upstream_ids:
            return []
        records = session.scalars(select(ArtifactRecord).where(ArtifactRecord.node_id.in_(upstream_ids)).order_by(ArtifactRecord.created_at)).all()
        return [self.artifact_store._to_manifest(record) for record in records]

    @staticmethod
    def _budgeted_upstream_artifacts(artifacts: list[ArtifactManifest], sources: list[ContextSource]) -> list[ArtifactManifest]:
        preview_by_id = {
            source.source_id: source.excerpt
            for source in sources
            if source.section == "upstream_artifacts" and source.included
        }
        manifests: list[ArtifactManifest] = []
        for artifact in artifacts:
            if artifact.id not in preview_by_id:
                continue
            manifests.append(
                ArtifactManifest.model_validate(
                    {
                        **artifact.model_dump(mode="python"),
                        "metadata": {
                            **(artifact.metadata or {}),
                            "content_preview": preview_by_id[artifact.id],
                        },
                    }
                )
            )
        return manifests

    @staticmethod
    def _included_retrieved_docs(sources: list[ContextSource]) -> list[dict]:
        items = []
        for source in sources:
            if source.section != "retrieved_docs" or not source.included:
                continue
            items.append(
                {
                    "source_type": source.source_type.value,
                    "source_id": source.source_id,
                    "path": source.path,
                    "score": source.score,
                    "excerpt": source.excerpt,
                    "metadata": source.metadata,
                    "scope": source.scope,
                    "source": source.path or source.source_type.value,
                    "content": source.excerpt,
                }
            )
        return items

    @staticmethod
    def _included_memories(sources: list[ContextSource]) -> list[str]:
        items = []
        for source in sources:
            if source.section not in {"cycle_summaries", "recent_memories", "project_template_profile"} or not source.included:
                continue
            items.append(source.excerpt)
        return items
