from functools import lru_cache

from app.agents.registry import build_default_registry
from app.config import get_settings
from app.services.artifact_store import ArtifactStore
from app.services.checkpoint_store import CheckpointStore
from app.services.context_budgeter import ContextBudgeter
from app.services.context_assembler import ContextAssembler
from app.services.context_document_service import ContextDocumentService
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
        settings = get_settings()
        self.provider_registry = ProviderRegistry()
        self.artifact_store = ArtifactStore()
        self.memory_service = MemoryService()
        self.context_document_service = ContextDocumentService()
        self.rag_service = RagService(self.context_document_service)
        self.requirement_intake = RequirementIntakeService(self.memory_service)
        self.event_bus = EventBus()
        self.checkpoint_store = CheckpointStore()
        self.graph_builder = WorkflowGraphBuilder()
        self.context_budgeter = ContextBudgeter(settings.context_char_budget)
        self.context_assembler = ContextAssembler(
            self.artifact_store,
            self.memory_service,
            self.context_document_service,
            self.context_budgeter,
        )
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
            rag_service=self.rag_service,
            context_document_service=self.context_document_service,
            checkpoint_store=self.checkpoint_store,
        )


@lru_cache(maxsize=1)
def get_container() -> ServiceContainer:
    return ServiceContainer()
