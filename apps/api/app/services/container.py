from functools import lru_cache

from app.agents.registry import build_default_registry
from app.services.artifact_store import ArtifactStore
from app.services.context_assembler import ContextAssembler
from app.services.event_bus import EventBus
from app.services.execution_runtime import ExecutionRuntime
from app.services.memory_service import MemoryService
from app.services.provider_registry import ProviderRegistry
from app.services.rag_service import RagService
from app.services.requirement_intake import RequirementIntakeService
from app.services.retry_recovery_manager import RetryRecoveryManager
from app.services.workflow_graph_builder import WorkflowGraphBuilder


class ServiceContainer:
    def __init__(self) -> None:
        self.provider_registry = ProviderRegistry()
        self.requirement_intake = RequirementIntakeService()
        self.artifact_store = ArtifactStore()
        self.memory_service = MemoryService()
        self.rag_service = RagService()
        self.event_bus = EventBus()
        self.graph_builder = WorkflowGraphBuilder()
        self.context_assembler = ContextAssembler(self.artifact_store, self.memory_service, self.rag_service)
        self.retry_manager = RetryRecoveryManager()
        self.runtime = ExecutionRuntime(
            registry=build_default_registry(),
            provider_registry=self.provider_registry,
            graph_builder=self.graph_builder,
            context_assembler=self.context_assembler,
            artifact_store=self.artifact_store,
            event_bus=self.event_bus,
            memory_service=self.memory_service,
            retry_manager=self.retry_manager,
        )


@lru_cache(maxsize=1)
def get_container() -> ServiceContainer:
    return ServiceContainer()
