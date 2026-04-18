from deps_workflow_manager.domain.model import (
    DocumentProcessingInfo,
    IDocumentProcessingInfoRepository,
)

__all__ = ["PipelineService"]


class PipelineService:
    def __init__(
        self,
        processing_repository: IDocumentProcessingInfoRepository,
    ) -> None:
        self._processing_repository = processing_repository

    def save_document_processing_info(self, info: DocumentProcessingInfo) -> None:
        self._processing_repository.save(info)
