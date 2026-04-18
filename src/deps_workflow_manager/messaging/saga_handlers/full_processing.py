from deps_workflow_manager.domain.model import Error, ErrorType

from ..commands import (
    CreateDocumentReply,
    PerformClassificationReply,
    PerformExtractionReply,
    PerformParsingReply,
    PerformUnificationReply,
    PerformValidationReply,
)
from ..sagas_data import FullProcessingSagaData

__all__ = ["FullProcessingHandlers"]


class FullProcessingHandlers:
    @staticmethod
    def create_document(data: FullProcessingSagaData, reply: CreateDocumentReply) -> None:
        data.document_id = reply.document_id

    @staticmethod
    def evaluate_unification_result(data: FullProcessingSagaData, reply: PerformUnificationReply) -> None:
        if reply.has_error:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)

    @staticmethod
    def evaluate_classification_result(data: FullProcessingSagaData, reply: PerformClassificationReply) -> None:
        if reply.document_type_id is not None:
            data.document_type_id = reply.document_type_id
        else:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)

    @staticmethod
    def evaluate_parsing_result(data: FullProcessingSagaData, reply: PerformParsingReply) -> None:
        if reply.has_error:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)

    @staticmethod
    def evaluate_extraction_result(data: FullProcessingSagaData, reply: PerformExtractionReply) -> None:
        if reply.has_error:
            data.error = Error(ErrorType(reply.error_type), reply.error_message)

    @staticmethod
    def save_validation_result(data: FullProcessingSagaData, reply: PerformValidationReply) -> None:
        data.validation_result = reply.result
