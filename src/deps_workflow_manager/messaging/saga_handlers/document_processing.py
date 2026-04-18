from deps_workflow_manager.domain.model import ContainerData

from ..commands import (
    CreateDocumentReply,
    PerformContainerUnificationReply,
    PerformValidationReply,
    PerformVersionClassificationReply,
)
from ..sagas_data import DocumentProcessingSagaData
from .error_handler_mixin import ErrorHandlerMixin

__all__ = ["DocumentProcessingHandlers"]


class DocumentProcessingHandlers(ErrorHandlerMixin):
    @staticmethod
    def create_document(data: DocumentProcessingSagaData, reply: CreateDocumentReply) -> None:
        data.document_id = reply.document_id

    @staticmethod
    def evaluate_container_unification_result(
        data: DocumentProcessingSagaData,
        reply: PerformContainerUnificationReply,
    ) -> None:
        DocumentProcessingHandlers.evaluate_error_from_reply(data, reply)
        if reply.container_type:
            attachments = reply.attachments
            data.container_data = ContainerData(
                type_=reply.container_type,
                metadata=reply.container_metadata,
                attachments=attachments,
            )

    @staticmethod
    def evaluate_version_classification_result(
        data: DocumentProcessingSagaData,
        reply: PerformVersionClassificationReply,
    ) -> None:
        DocumentProcessingHandlers.evaluate_error_from_reply(data, reply)
        if (version_id := reply.version_id) is not None:
            data.template_version_id = version_id

    @staticmethod
    def save_validation_result(data: DocumentProcessingSagaData, reply: PerformValidationReply) -> None:
        data.record_validation_result(reply.result)
