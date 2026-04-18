import logging

from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import PerformValidationReply, PerformVersionClassificationReply
from ..events import DocumentProcessingFailed, DocumentProcessingSucceed
from ..saga_handlers import TemplateProcessingHandlers
from ..sagas_data import TemplateProcessingSagaData, TemplateProcessingSteps

__all__ = ["TemplateProcessingSaga"]


class TemplateProcessingSaga(SimpleSaga[TemplateProcessingSagaData]):
    DOCUMENTS_DESTINATION: str = "Documents"

    def __init__(self, domain_event_publisher: DomainEventPublisher, steps: TemplateProcessingSteps) -> None:
        self._dep = domain_event_publisher

        self._saga_definition = (
            self.step()
            .invoke_local(
                steps.create_document,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.update_state,
                predicate=TemplateProcessingSagaData.is_invoke_state_update,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.perform_unification,
                predicate=TemplateProcessingSagaData.is_invoke_unifier,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.perform_preprocessing,
                predicate=TemplateProcessingSagaData.is_invoke_preprocessor,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.update_state,
                predicate=TemplateProcessingSagaData.is_invoke_state_update,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.perform_version_classification,
                predicate=TemplateProcessingSagaData.is_invoke_version_classification,
            )
            .on_reply(PerformVersionClassificationReply, TemplateProcessingHandlers.perform_version_classification)
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.update_state,
                predicate=TemplateProcessingSagaData.is_invoke_state_update,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.perform_template_extraction,
                predicate=TemplateProcessingSagaData.is_invoke_extraction,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.update_state,
                predicate=TemplateProcessingSagaData.is_invoke_validation_state_update,
            )
            .step()
            .invoke_participant(
                TemplateProcessingSagaData.perform_validation,
                predicate=TemplateProcessingSagaData.is_invoke_validation,
            )
            .on_reply(PerformValidationReply, TemplateProcessingHandlers.save_validation_result)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: TemplateProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)
        self._dep.publish(
            self.DOCUMENTS_DESTINATION,
            data.document_id,
            [DocumentProcessingSucceed(data.document_id, data.document_type_id)],
        )

    def on_saga_failed(self, saga_id: str, data: TemplateProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is failed", saga_id, data.document_id)
        self._dep.publish(
            self.DOCUMENTS_DESTINATION,
            data.document_id,
            [DocumentProcessingFailed(data.document_id, f"Failed to process document {data.document_id}.")],
        )

    def on_saga_rolled_back(self, saga_id: str, data: TemplateProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
        self._dep.publish(
            self.DOCUMENTS_DESTINATION,
            data.document_id,
            [DocumentProcessingFailed(data.document_id, f"Failed to process document {data.document_id}.")],
        )
