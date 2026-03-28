from app.agents.langchain_agents import LangChainLCELAgent, LangChainToolAgent
from app.models.schemas import Role


def build_default_registry() -> dict[Role, object]:
    return {
        Role.PC: LangChainLCELAgent(Role.PC),
        Role.CA: LangChainLCELAgent(Role.CA),
        Role.FD: LangChainToolAgent(Role.FD),
        Role.BD: LangChainToolAgent(Role.BD),
        Role.DE: LangChainToolAgent(Role.DE),
        Role.QT: LangChainToolAgent(Role.QT),
    }
