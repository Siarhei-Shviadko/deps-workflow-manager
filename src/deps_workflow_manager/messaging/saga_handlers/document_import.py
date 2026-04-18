from deps_workflow_manager.messaging.commands import ImportDocumentsReply

from ..sagas_data import DocumentsImportSagaData

__all__ = ["DocumentsImportHandlers"]


class DocumentsImportHandlers:
    @staticmethod
    def save_document_data(data: DocumentsImportSagaData, reply: ImportDocumentsReply) -> None:
        data.documents = reply.documents
