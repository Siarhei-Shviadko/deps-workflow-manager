import logging

from deps_workflow_manager.domain.exceptions import DocumentTypeHasAssignedDocuments
from deps_workflow_manager.infrastructure.services import (
    DocumentService,
    TemplateService,
)

__all__ = ["TemplateDeletionSteps"]

from .template_deletion_data import TemplateDeletionSagaData


class TemplateDeletionSteps:
    def __init__(
        self,
        template_service: TemplateService,
        document_service: DocumentService,
    ):
        self._template_service = template_service
        self._document_service = document_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def check_doc_type_has_docs(self, data: TemplateDeletionSagaData) -> None:
        if self._document_service.document_type_has_docs(data.template_id):
            raise DocumentTypeHasAssignedDocuments(f"{data.template_id} has documents")

    def delete_template(self, data: TemplateDeletionSagaData) -> None:
        self._logger.info(f"Deleting template {data.template_id}")
        self._template_service.delete_template(data.template_id)
