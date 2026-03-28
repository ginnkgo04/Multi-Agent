from app.agents.base import AgentProfile, WorkflowAgent
from app.models.schemas import Role


def build_default_registry() -> dict[Role, WorkflowAgent]:
    return {
        Role.PC: WorkflowAgent(
            AgentProfile(
                role=Role.PC,
                system_prompt="You are the Product Coordinator. Break requirements into an executable shared plan with acceptance criteria.",
                artifact_prefix="requirement-brief",
            )
        ),
        Role.CA: WorkflowAgent(
            AgentProfile(
                role=Role.CA,
                system_prompt="You are the Chief Architect. Produce architecture decisions, interfaces, and a coordination plan.",
                artifact_prefix="architecture-plan",
            )
        ),
        Role.FD: WorkflowAgent(
            AgentProfile(
                role=Role.FD,
                system_prompt="You are the Frontend Developer. Translate architecture into frontend implementation artifacts.",
                artifact_prefix="frontend-plan",
            )
        ),
        Role.BD: WorkflowAgent(
            AgentProfile(
                role=Role.BD,
                system_prompt="You are the Backend Developer. Produce backend implementation artifacts and API changes.",
                artifact_prefix="backend-plan",
            )
        ),
        Role.DE: WorkflowAgent(
            AgentProfile(
                role=Role.DE,
                system_prompt="You are the Delivery Engineer. Integrate outputs, verify readiness, and prepare delivery artifacts.",
                artifact_prefix="delivery-bundle",
            )
        ),
        Role.QT: WorkflowAgent(
            AgentProfile(
                role=Role.QT,
                system_prompt="You are the Quality Tester. Evaluate implementation quality, decide pass/fail, and issue remediation requirements.",
                artifact_prefix="quality-report",
            )
        ),
    }
