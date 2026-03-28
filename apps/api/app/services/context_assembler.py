from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.records import ArtifactRecord, CycleRecord, NodeExecutionRecord, RunRecord
from app.models.schemas import AgentTaskContext, ArtifactManifest, ProviderConfig, Role
from app.services.artifact_store import ArtifactStore
from app.services.memory_service import MemoryService
from app.services.workflow_graph_builder import role_dependencies_for_cycle


class ContextAssembler:
    def __init__(self, artifact_store: ArtifactStore, memory_service: MemoryService, rag_service) -> None:
        self.artifact_store = artifact_store
        self.memory_service = memory_service
        self.rag_service = rag_service

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
        upstream_roles = role_dependencies_for_cycle(cycle.cycle_index)[Role(node.role)]
        upstream_nodes = session.scalars(
            select(NodeExecutionRecord).where(
                NodeExecutionRecord.cycle_id == cycle.id,
                NodeExecutionRecord.role.in_([role.value for role in upstream_roles]),
            )
        ).all()
        upstream_ids = [upstream.id for upstream in upstream_nodes]
        upstream_artifacts = self._artifact_manifests(session, upstream_ids)
        shared_plan = self._extract_shared_plan(session, cycle.id)
        summaries = self.memory_service.summarize_cycles(session, run.id)
        memories = summaries + self.memory_service.list_recent(session, run.id)
        retrieved_context = await self.rag_service.retrieve(
            session,
            run.project_id,
            query=f"{run.requirement}\n{cycle.remediation_requirement or ''}\n{node.role}",
            embedding_provider=embedding_provider,
        )
        task_spec = dict(node.task_spec or {})
        return AgentTaskContext(
            role=Role(node.role),
            run_id=run.id,
            cycle_id=cycle.id,
            cycle_index=cycle.cycle_index,
            task_spec=task_spec,
            shared_plan=shared_plan,
            upstream_artifacts=upstream_artifacts,
            retrieved_context=retrieved_context,
            provider_config=chat_config,
            memories=memories,
            original_requirement=run.requirement,
        )

    def _extract_shared_plan(self, session: Session, cycle_id: str) -> dict:
        nodes = session.scalars(
            select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle_id, NodeExecutionRecord.role.in_([Role.PC.value, Role.CA.value]))
        ).all()
        for node in reversed(nodes):
            payload = node.result_payload or {}
            if "shared_plan" in payload:
                return payload["shared_plan"]
            if payload:
                return payload
        return {}

    def _artifact_manifests(self, session: Session, node_ids: list[str]) -> list[ArtifactManifest]:
        if not node_ids:
            return []
        records = session.scalars(select(ArtifactRecord).where(ArtifactRecord.node_id.in_(node_ids)).order_by(ArtifactRecord.created_at)).all()
        return [self.artifact_store._to_manifest(record) for record in records]
