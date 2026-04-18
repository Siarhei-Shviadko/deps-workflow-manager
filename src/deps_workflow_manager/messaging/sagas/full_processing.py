import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import (
    CreateDocumentReply,
    PerformClassificationReply,
    PerformExtractionReply,
    PerformParsingReply,
    PerformUnificationReply,
    PerformValidationReply,
)
from ..saga_handlers import FullProcessingHandlers
from ..sagas_data import FullProcessingSagaData, FullProcessingSteps

__all__ = ["FullProcessingSaga"]


class FullProcessingSaga(SimpleSaga[FullProcessingSagaData]):
    DOCUMENTS_DESTINATION: str = "Documents"

    def __init__(self, steps: FullProcessingSteps) -> None:
        self._saga_definition = (
            # Creation
            self.step()
            .invoke_participant(
                FullProcessingSagaData.create_document,
                predicate=FullProcessingSagaData.is_invoke_document_creation,
            )
            .on_reply(CreateDocumentReply, FullProcessingHandlers.create_document)
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_document_creation,
            )
            # Unification
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_unification,
                predicate=FullProcessingSagaData.is_invoke_unifier,
            )
            .on_reply(PerformUnificationReply, FullProcessingHandlers.evaluate_unification_result)
            # Load workflow configuration
            .step()
            .invoke_local(steps.set_processing_configuration)
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_unifier,
            )
            # Classification
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_classification,
                predicate=FullProcessingSagaData.is_invoke_classification,
            )
            .on_reply(PerformClassificationReply, FullProcessingHandlers.evaluate_classification_result)
            # Load workflow configuration
            .step()
            .invoke_local(steps.set_processing_configuration)
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_classification,
            )
            # Image preprocessing
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_image_preprocessing,
                predicate=FullProcessingSagaData.is_invoke_image_preprocessing,
            )
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_image_preprocessing,
            )
            # Parsing
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_parsing,
                predicate=FullProcessingSagaData.is_invoke_parsing,
            )
            .on_reply(PerformParsingReply, FullProcessingHandlers.evaluate_parsing_result)
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_parsing,
            )
            # Extraction
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_extraction,
                predicate=FullProcessingSagaData.is_invoke_extraction,
            )
            .on_reply(PerformExtractionReply, FullProcessingHandlers.evaluate_extraction_result)
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_extraction,
            )
            # Postprocessing
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_postprocessing,
                predicate=FullProcessingSagaData.is_invoke_postprocessing,
            )
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_postprocessing,
            )
            # Validation
            .step()
            .invoke_participant(
                FullProcessingSagaData.perform_validation,
                predicate=FullProcessingSagaData.is_invoke_validation,
            )
            .on_reply(PerformValidationReply, FullProcessingHandlers.save_validation_result)
            .step()
            .invoke_participant(
                FullProcessingSagaData.update_state,
                predicate=FullProcessingSagaData.is_invoke_validation,
            )
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: FullProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)

    def on_saga_failed(self, saga_id: str, data: FullProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is failed", saga_id, data.document_id)

    def on_saga_rolled_back(self, saga_id: str, data: FullProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
