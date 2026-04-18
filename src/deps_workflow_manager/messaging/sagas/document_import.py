import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import ImportDocumentsReply
from ..saga_handlers import DocumentsImportHandlers
from ..sagas_data import DocumentsImportSagaData

__all__ = ["DocumentsImportSaga"]


class DocumentsImportSaga(SimpleSaga[DocumentsImportSagaData]):
    def __init__(self) -> None:
        self._saga_definition = (
            self.step()
            .invoke_participant(DocumentsImportSagaData.import_documents)
            .on_reply(ImportDocumentsReply, DocumentsImportHandlers.save_document_data)
            .step()
            .invoke_participant(DocumentsImportSagaData.process_documents)
            .build()
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: DocumentsImportSagaData) -> None:
        self._logger.info("DocumentsImportSaga %s is completed successfully", saga_id)

    def on_saga_failed(self, saga_id: str, data: DocumentsImportSagaData) -> None:
        self._logger.error("DocumentsImportSaga %s is failed", saga_id)

    def on_saga_rolled_back(self, saga_id: str, data: DocumentsImportSagaData) -> None:
        self._logger.error("DocumentsImportSaga %s is rolled back", saga_id)
