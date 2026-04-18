import logging

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import PerformValidationReply
from ..events import DocumentReviewCompleted
from ..saga_handlers import CompleteReviewHandlers
from ..sagas_data import CompleteReviewSagaData, CompleteReviewSteps

__all__ = ["CompleteReviewSaga"]


class CompleteReviewSaga(SimpleSaga[CompleteReviewSagaData]):
    DOCUMENTS_DESTINATION: str = "Documents"

    def __init__(self, steps: CompleteReviewSteps, domain_event_publisher: DomainEventPublisher) -> None:
        self._dep = domain_event_publisher
        self._saga_definition = (
            self.step()
            .invoke_local(steps.set_validation_state)
            .with_compensation(steps.set_validation_failed_state)
            .step()
            .invoke_participant(CompleteReviewSagaData.perform_validation)
            .on_reply(PerformValidationReply, CompleteReviewHandlers.save_validation_result)
            .step()
            .invoke_participant(
                CompleteReviewSagaData.unassign_reviewer,
                predicate=CompleteReviewSagaData.should_unassign_reviewer,
            )
            .step()
            .invoke_participant(
                CompleteReviewSagaData.update_state,
                predicate=CompleteReviewSagaData.is_invoke_state_update,
            )
            .build()
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: CompleteReviewSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)
        if data.validation_result:
            self._dep.publish(
                self.DOCUMENTS_DESTINATION,
                data.document_id,
                [DocumentReviewCompleted(document_id=data.document_id, document_metadata=data.metadata)],
            )

    def on_saga_failed(self, saga_id: str, data: CompleteReviewSagaData) -> None:
        self._logger.error("Saga: %s for document: %s is failed", saga_id, data.document_id)

    def on_saga_rolled_back(self, saga_id: str, data: CompleteReviewSagaData) -> None:
        self._logger.error("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
