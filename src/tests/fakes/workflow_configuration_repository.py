from typing import Optional

from deps_workflow_manager.domain.model import (
    DocumentTypeInfo,
    IWorkflowConfigurationRepository,
    WorkflowConfiguration,
)

__all__ = ["FakeWorkflowConfigurationRepository"]


class FakeWorkflowConfigurationRepository(IWorkflowConfigurationRepository):
    def __init__(self, db: dict[tuple[str, str], WorkflowConfiguration] = None) -> None:
        self.db = db if db is not None else {}

    def find(self, tenant_id: str, document_type_id: str) -> Optional[WorkflowConfiguration]:
        if (configuration := self.db.get((tenant_id, document_type_id))) is not None:
            return configuration

        return None

    def save(self, configuration: WorkflowConfiguration) -> None:
        self.db[(configuration.tenant_id, configuration.document_type_id)] = configuration

    def save_for(self, document_types: list[DocumentTypeInfo]) -> None:
        for document_type in document_types:
            key = (document_type.tenant_id, document_type.document_type_id)
            if existing_config := self.db.get(key):
                existing_config.extraction_type = document_type.extraction_type
                existing_config.image_transformations = document_type.image_transformations
                existing_config.llm_type = document_type.llm_type
                existing_config.engine = document_type.engine
            else:
                self.db[key] = WorkflowConfiguration(
                    tenant_id=document_type.tenant_id,
                    document_type_id=document_type.document_type_id,
                    extraction_type=document_type.extraction_type,
                    image_transformations=document_type.image_transformations,
                    llm_type=document_type.llm_type,
                    engine=document_type.engine,
                )

    def delete(self, tenant_id: str, document_type_id: str) -> None:
        self.db.pop((tenant_id, document_type_id), None)
