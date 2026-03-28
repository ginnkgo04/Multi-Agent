from app.models.schemas import Role
from app.services.workflow_graph_builder import role_dependencies_for_cycle, role_order_for_cycle


def test_remediation_cycle_restarts_from_ca() -> None:
    order = role_order_for_cycle(2)

    assert order[0] is Role.CA
    assert Role.PC not in order
    assert role_dependencies_for_cycle(2)[Role.CA] == []
