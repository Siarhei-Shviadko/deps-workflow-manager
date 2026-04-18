from typing import Optional, Protocol

from .workflow_configuration import DocumentTypeInfo, WorkflowConfiguration

__all__ = ["IWorkflowConfigurationRepository"]


class IWorkflowConfigurationRepository(Protocol):
    def find(self, tenant_id: str, document_type_id: str) -> Optional[WorkflowConfiguration]:
        pass

    def find_all(self, tenant_id: str) -> list[WorkflowConfiguration]:
        pass

    def save(self, configuration: WorkflowConfiguration) -> None:
        pass

    def save_for(self, document_types: list[DocumentTypeInfo]) -> None:
        pass

    def delete(self, tenant_id: str, document_type_id: str) -> None:
        pass
