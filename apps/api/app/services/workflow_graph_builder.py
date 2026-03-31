from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.records import CycleRecord, NodeExecutionRecord
from app.models.schemas import CycleStatus, GraphResponse, NodeStatus, Role, WorkflowEdgeView, WorkflowNodeView
from app.services.batch_scheduler import BatchScheduler

INITIAL_ROLE_ORDER = [Role.PC, Role.CA, Role.FD, Role.BD, Role.DE, Role.QT]
INITIAL_ROLE_DEPENDENCIES: dict[Role, list[Role]] = {
    Role.PC: [],
    Role.CA: [Role.PC],
    Role.FD: [Role.CA],
    Role.BD: [Role.CA],
    Role.DE: [Role.FD, Role.BD],
    Role.QT: [Role.DE],
}
REMEDIATION_ROLE_ORDER = [Role.CA, Role.FD, Role.BD, Role.DE, Role.QT]
REMEDIATION_ROLE_DEPENDENCIES: dict[Role, list[Role]] = {
    Role.CA: [],
    Role.FD: [Role.CA],
    Role.BD: [Role.CA],
    Role.DE: [Role.FD, Role.BD],
    Role.QT: [Role.DE],
}


def role_order_for_cycle(cycle_index: int) -> list[Role]:
    return INITIAL_ROLE_ORDER if cycle_index == 1 else REMEDIATION_ROLE_ORDER


def role_dependencies_for_cycle(cycle_index: int) -> dict[Role, list[Role]]:
    return INITIAL_ROLE_DEPENDENCIES if cycle_index == 1 else REMEDIATION_ROLE_DEPENDENCIES


class WorkflowGraphBuilder:
    def __init__(self) -> None:
        self.scheduler = BatchScheduler()

    def ensure_cycle_nodes(self, session: Session, run_id: str, cycle: CycleRecord) -> tuple[list[NodeExecutionRecord], list[tuple[str, str]]]:
        existing_nodes = session.scalars(
            select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id).order_by(NodeExecutionRecord.batch_index)
        ).all()
        if existing_nodes:
            return list(existing_nodes), self._build_edges(existing_nodes, cycle.cycle_index)

        role_order = role_order_for_cycle(cycle.cycle_index)
        role_dependencies = role_dependencies_for_cycle(cycle.cycle_index)
        node_dicts = [{"id": role.value, "role": role.value} for role in role_order]
        edges_for_batches = [(source.value, target.value) for target, dependencies in role_dependencies.items() for source in dependencies]
        batches = self.scheduler.build_batches(node_dicts, edges_for_batches)
        batch_lookup = {node_id: index for index, batch in enumerate(batches) for node_id in batch}

        for role in role_order:
            task_spec = {
                "dependencies": [dependency.value for dependency in role_dependencies[role]],
                "remediation_requirement": cycle.remediation_requirement,
            }
            session.add(
                NodeExecutionRecord(
                    run_id=run_id,
                    cycle_id=cycle.id,
                    role=role.value,
                    batch_index=batch_lookup[role.value],
                    status=NodeStatus.PENDING.value,
                    task_spec=task_spec,
                )
            )
        if cycle.status == CycleStatus.PENDING.value:
            cycle.status = CycleStatus.RUNNING.value
        session.commit()
        nodes = list(session.scalars(
            select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id).order_by(NodeExecutionRecord.batch_index)
        ).all())
        return nodes, self._build_edges(nodes, cycle.cycle_index)

    def graph_view(self, session: Session, run_id: str) -> GraphResponse:
        cycles = session.scalars(select(CycleRecord).where(CycleRecord.run_id == run_id).order_by(CycleRecord.cycle_index)).all()
        nodes: list[WorkflowNodeView] = []
        edges: list[WorkflowEdgeView] = []
        for cycle in cycles:
            cycle_nodes = session.scalars(
                select(NodeExecutionRecord).where(NodeExecutionRecord.cycle_id == cycle.id).order_by(NodeExecutionRecord.batch_index)
            ).all()
            for node in cycle_nodes:
                nodes.append(
                    WorkflowNodeView(
                        id=node.id,
                        role=Role(node.role),
                        cycle_id=node.cycle_id,
                        cycle_index=cycle.cycle_index,
                        batch_index=node.batch_index,
                        status=NodeStatus(node.status),
                        retry_count=node.retry_count,
                        error_message=node.error_message,
                        started_at=node.started_at,
                        finished_at=node.finished_at,
                    )
                )
            for source, target in self._build_edges(cycle_nodes, cycle.cycle_index):
                edges.append(WorkflowEdgeView(source=source, target=target))
        return GraphResponse(run_id=run_id, nodes=nodes, edges=edges)

    def _build_edges(self, nodes: Iterable[NodeExecutionRecord], cycle_index: int) -> list[tuple[str, str]]:
        by_role = {node.role: node.id for node in nodes}
        edges: list[tuple[str, str]] = []
        for role, dependencies in role_dependencies_for_cycle(cycle_index).items():
            for dependency in dependencies:
                if dependency.value in by_role and role.value in by_role:
                    edges.append((by_role[dependency.value], by_role[role.value]))
        return edges
