import logging

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import PerformValidationReply
from ..events import DocumentReviewCompleted
from ..saga_handlers import ValidateHandlers
from ..sagas_data import ValidateSagaData, ValidateSteps

__all__ = ["ValidateSaga"]


class ValidateSaga(SimpleSaga[ValidateSagaData]):
    DOCUMENTS_DESTINATION: str = "Documents"

    def __init__(self, steps: ValidateSteps, domain_event_publisher: DomainEventPublisher) -> None:
        self._dep = domain_event_publisher
        self._saga_definition = (
            self.step()
            .invoke_local(steps.set_validation_state)
            .with_compensation(steps.set_validation_failed_state)
            .step()
            .invoke_participant(ValidateSagaData.perform_validation)
            .on_reply(PerformValidationReply, ValidateHandlers.save_validation_result)
            .step()
            .invoke_participant(
                ValidateSagaData.update_state,
                predicate=ValidateSagaData.is_invoke_state_update,
            )
            .build()
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: ValidateSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)
        if data.validation_result:
            self._dep.publish(
                self.DOCUMENTS_DESTINATION,
                data.document_id,
                [DocumentReviewCompleted(document_id=data.document_id, document_metadata=data.metadata)],
            )

    def on_saga_failed(self, saga_id: str, data: ValidateSagaData) -> None:
        self._logger.error("Saga: %s for document: %s is failed", saga_id, data.document_id)

    def on_saga_rolled_back(self, saga_id: str, data: ValidateSagaData) -> None:
        self._logger.error("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
