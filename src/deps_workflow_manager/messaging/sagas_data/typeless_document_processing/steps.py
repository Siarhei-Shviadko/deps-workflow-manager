import logging

from deps_workflow_manager.application.pipeline_service import PipelineService

from .typeless_document_processing import TypelessDocumentProcessingSagaData

__all__ = ["TypelessDocumentProcessingSteps"]


class TypelessDocumentProcessingSteps:
    def __init__(self, pipeline_service: PipelineService) -> None:
        self._pipeline_service = pipeline_service

        self._logger = logging.getLogger(self.__class__.__name__)

    def save_document_processing_info(self, data: TypelessDocumentProcessingSagaData) -> None:
        self._logger.info(f"Saving document processing info for document: {data.document_processing_info!r}")
        self._pipeline_service.save_document_processing_info(data.document_processing_info)
