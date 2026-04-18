from ..commands import (
    CreateDocumentReply,
    PerformValidationReply,
    PerformVersionClassificationReply,
)
from ..sagas_data import TemplateProcessingSagaData

__all__ = ["TemplateProcessingHandlers"]


class TemplateProcessingHandlers:
    @staticmethod
    def create_document(data: TemplateProcessingSagaData, reply: CreateDocumentReply) -> None:
        data.document_id = reply.document_id

    @staticmethod
    def perform_version_classification(
        data: TemplateProcessingSagaData,
        reply: PerformVersionClassificationReply,
    ) -> None:
        data.version_id = reply.version_id

    @staticmethod
    def save_validation_result(data: TemplateProcessingSagaData, reply: PerformValidationReply) -> None:
        data.validation_result = reply.result
