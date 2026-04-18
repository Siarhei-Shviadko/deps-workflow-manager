import logging

from deps_workflow_manager.domain.exceptions import RestClientError
from deps_workflow_manager.infrastructure.services import DocumentService

from .validate import ValidateSagaData

__all__ = ["ValidateSteps"]


class ValidateSteps:
    def __init__(self, document_service: DocumentService):
        self._document_service = document_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def set_validation_state(self, data: ValidateSagaData) -> None:
        try:
            self._document_service.update_document_detail(data.document_id, {"state": data.next_state})
            data.update_current_state()
        except RestClientError as err:
            self._logger.error(f"Can't set validation state for document {data.document_id}. {str(err)}", exc_info=True)
            raise

    def set_validation_failed_state(self, data: ValidateSagaData) -> None:
        try:
            self._document_service.update_document_detail(data.document_id, {"state": data.validation_failed_next_step})
        except RestClientError as err:
            self._logger.error(f"Can't set inReview state for document {data.document_id}. {str(err)}", exc_info=True)
            raise
