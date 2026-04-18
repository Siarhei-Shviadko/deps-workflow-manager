import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import (
    AssignDocumentTypeReply,
    CreateDocumentReply,
    PerformClassificationReply,
    PerformContainerUnificationReply,
    PerformParsingReply,
    PerformUnificationReply,
    UpdateContainerDataReply,
)
from ..saga_handlers import TypelessDocumentProcessingHandlers as Handlers
from ..sagas_data import TypelessDocumentProcessingSagaData as SagaData
from ..sagas_data import TypelessDocumentProcessingSteps as Steps

__all__ = ["TypelessDocumentProcessingSaga"]


class TypelessDocumentProcessingSaga(SimpleSaga[SagaData]):
    def __init__(self, steps: Steps) -> None:
        self._saga_definition = (
            # Creation
            self.step()
            .invoke_participant(
                SagaData.create_document,
                predicate=SagaData.is_invoke_document_creation,
            )
            .on_reply(CreateDocumentReply, Handlers.create_document)
            .step()
            .invoke_local(
                steps.save_document_processing_info,
            )
            .step()
            .invoke_participant(
                SagaData.set_state,
                predicate=SagaData.is_not_invoke_document_creation,
            )
            .step()
            .invoke_participant(
                SagaData.update_state,
                predicate=SagaData.is_new_or_unification_without_unifier,
            )
            # Unification
            .step()
            .invoke_participant(
                SagaData.perform_unification,
                predicate=SagaData.is_invoke_unifier,
            )
            .on_reply(PerformUnificationReply, Handlers.evaluate_error_from_reply)
            .on_reply(PerformContainerUnificationReply, Handlers.evaluate_container_unification_result)
            .step()
            .invoke_participant(
                SagaData.update_container_data,
                predicate=SagaData.is_container_type,
            )
            .on_reply(UpdateContainerDataReply, Handlers.evaluate_error_from_reply)
            # Start attachment processing
            .step()
            .invoke_participant(
                SagaData.start_attachments_processing,
                predicate=SagaData.is_attachment_processing_possible,
            )
            .step()
            .invoke_participant(
                SagaData.update_state,
                predicate=SagaData.is_invoke_unifier,
            )
            # Image preprocessing
            .step()
            .invoke_participant(
                SagaData.perform_image_preprocessing,
                predicate=SagaData.is_invoke_image_preprocessing,
            )
            .step()
            .invoke_participant(
                SagaData.update_state,
                predicate=SagaData.is_invoke_image_preprocessing,
            )
            # Parsing
            .step()
            .invoke_participant(
                SagaData.perform_parsing,
                predicate=SagaData.is_invoke_parsing,
            )
            .on_reply(PerformParsingReply, Handlers.evaluate_error_from_reply)
            .step()
            .invoke_participant(
                SagaData.update_state,
                predicate=SagaData.is_invoke_parsing_completion,
            )
            # Classification
            .step()
            .invoke_participant(
                SagaData.perform_classification,
                predicate=SagaData.is_invoke_classification,
            )
            .on_reply(PerformClassificationReply, Handlers.evaluate_classification_result)
            .step()
            .invoke_participant(
                SagaData.assign_document_type,
                predicate=SagaData.is_classification_successful,
            )
            .on_reply(AssignDocumentTypeReply, Handlers.evaluate_error_from_reply)
            .step()
            .invoke_participant(
                SagaData.update_state,
                predicate=SagaData.is_invoke_classification,
            )
            # Start full processing
            .step()
            .invoke_participant(
                SagaData.start_document_processing,
                predicate=SagaData.is_start_document_processing_possible,
            )
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: SagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)

    def on_saga_failed(self, saga_id: str, data: SagaData) -> None:
        self._logger.info("Saga: %s for document: %s is failed", saga_id, data.document_id)

    def on_saga_rolled_back(self, saga_id: str, data: SagaData) -> None:
        self._logger.info("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
