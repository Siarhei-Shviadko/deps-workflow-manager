from ..commands import CreateDocumentReply, PerformValidationReply
from ..sagas_data import PluginProcessingSagaData

__all__ = ["PluginProcessingHandlers"]


class PluginProcessingHandlers:
    @staticmethod
    def create_document(data: PluginProcessingSagaData, reply: CreateDocumentReply) -> None:
        data.document_id = reply.document_id

    @staticmethod
    def save_validation_result(data: PluginProcessingSagaData, reply: PerformValidationReply) -> None:
        data.validation_result = reply.result
