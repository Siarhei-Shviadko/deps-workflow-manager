import logging

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import PerformValidationReply
from ..events import DocumentProcessingFailed, DocumentProcessingSucceed
from ..saga_handlers import PluginProcessingHandlers
from ..sagas_data import PluginProcessingSagaData, PluginProcessingSteps

__all__ = ["PluginProcessingSaga"]


class PluginProcessingSaga(SimpleSaga[PluginProcessingSagaData]):
    DOCUMENTS_DESTINATION: str = "Documents"

    def __init__(self, domain_event_publisher: DomainEventPublisher, steps: PluginProcessingSteps) -> None:
        self._dep = domain_event_publisher

        self._saga_definition = (
            self.step()
            .invoke_local(
                steps.create_document,
            )
            .step()
            .invoke_participant(
                PluginProcessingSagaData.update_state,
                predicate=PluginProcessingSagaData.is_invoke_state_update,
            )
            .step()
            .invoke_participant(
                PluginProcessingSagaData.perform_unification,
                predicate=PluginProcessingSagaData.is_invoke_unifier,
            )
            .step()
            .invoke_participant(
                PluginProcessingSagaData.update_state,
                predicate=PluginProcessingSagaData.is_invoke_state_update,
            )
            .step()
            .invoke_participant(
                PluginProcessingSagaData.perform_extraction,
                predicate=PluginProcessingSagaData.is_invoke_extraction,
            )
            .step()
            .invoke_participant(
                PluginProcessingSagaData.update_state,
                predicate=PluginProcessingSagaData.is_invoke_validation_state_update,
            )
            .step()
            .invoke_participant(
                PluginProcessingSagaData.perform_validation,
                predicate=PluginProcessingSagaData.is_invoke_validation,
            )
            .on_reply(PerformValidationReply, PluginProcessingHandlers.save_validation_result)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: PluginProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)
        self._dep.publish(
            self.DOCUMENTS_DESTINATION,
            data.document_id,
            [DocumentProcessingSucceed(data.document_id, data.document_type_id)],
        )

    def on_saga_failed(self, saga_id: str, data: PluginProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is failed", saga_id, data.document_id)
        self._dep.publish(
            self.DOCUMENTS_DESTINATION,
            data.document_id,
            [DocumentProcessingFailed(data.document_id, f"Failed to process document {data.document_id}.")],
        )

    def on_saga_rolled_back(self, saga_id: str, data: PluginProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
        self._dep.publish(
            self.DOCUMENTS_DESTINATION,
            data.document_id,
            [DocumentProcessingFailed(data.document_id, f"Failed to process document {data.document_id}.")],
        )
