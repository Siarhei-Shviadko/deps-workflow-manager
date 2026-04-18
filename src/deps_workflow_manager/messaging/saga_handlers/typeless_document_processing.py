from deps_workflow_manager.domain.model import ContainerData

from ..commands import (
    CreateDocumentReply,
    PerformClassificationReply,
    PerformContainerUnificationReply,
)
from ..sagas_data import TypelessDocumentProcessingSagaData
from .error_handler_mixin import ErrorHandlerMixin

__all__ = ["TypelessDocumentProcessingHandlers"]


class TypelessDocumentProcessingHandlers(ErrorHandlerMixin):
    @staticmethod
    def create_document(data: TypelessDocumentProcessingSagaData, reply: CreateDocumentReply) -> None:
        data.document_id = reply.document_id

    @staticmethod
    def evaluate_container_unification_result(
        data: TypelessDocumentProcessingSagaData,
        reply: PerformContainerUnificationReply,
    ) -> None:
        TypelessDocumentProcessingHandlers.evaluate_error_from_reply(data, reply)
        if reply.container_type:
            attachments = reply.attachments
            data.container_data = ContainerData(
                type_=reply.container_type,
                metadata=reply.container_metadata,
                attachments=attachments,
            )

    @staticmethod
    def evaluate_classification_result(
        data: TypelessDocumentProcessingSagaData,
        reply: PerformClassificationReply,
    ) -> None:
        TypelessDocumentProcessingHandlers.evaluate_error_from_reply(data, reply)
        if reply.document_type_id is not None:
            data.document_type_id = reply.document_type_id
