import logging

from deps_workflow_manager.application.pipeline_service import PipelineService
from deps_workflow_manager.domain.model import IWorkflowConfigurationRepository

from .document_processing import DocumentProcessingSagaData

__all__ = ["DocumentProcessingSteps"]


class DocumentProcessingSteps:
    def __init__(
        self,
        workflow_configuration_repository: IWorkflowConfigurationRepository,
        pipeline_service: PipelineService,
    ) -> None:
        self._workflow_configuration_repository = workflow_configuration_repository
        self._pipeline_service = pipeline_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def set_processing_configuration(self, data: DocumentProcessingSagaData) -> None:
        config = self._workflow_configuration_repository.find(
            data.tenant_id,
            data.document_type_id,
        )
        data.set_workflow_configuration(
            config,
        )

    def save_document_processing_info(self, data: DocumentProcessingSagaData) -> None:
        self._pipeline_service.save_document_processing_info(data.document_processing_info)
