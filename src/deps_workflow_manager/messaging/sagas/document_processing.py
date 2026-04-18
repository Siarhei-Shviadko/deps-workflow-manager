import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import (
    CreateDocumentReply,
    PerformContainerUnificationReply,
    PerformExportingReply,
    PerformExtractionReply,
    PerformParsingReply,
    PerformUnificationReply,
    PerformValidationReply,
    PerformVersionClassificationReply,
    UpdateContainerDataReply,
)
from ..saga_handlers import DocumentProcessingHandlers as Handlers
from ..sagas_data import DocumentProcessingSagaData, DocumentProcessingSteps

__all__ = ["DocumentProcessingSaga"]


class DocumentProcessingSaga(SimpleSaga[DocumentProcessingSagaData]):
    DOCUMENTS_DESTINATION: str = "Documents"

    def __init__(self, steps: DocumentProcessingSteps) -> None:
        self._saga_definition = (
            # Load workflow configuration
            self.step()
            .invoke_local(steps.set_processing_configuration)
            # Creation
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.create_document,
                predicate=DocumentProcessingSagaData.is_invoke_document_creation,
            )
            .on_reply(CreateDocumentReply, Handlers.create_document)
            .step()
            .invoke_local(
                steps.save_document_processing_info,
            )
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.set_state,
                predicate=DocumentProcessingSagaData.is_not_invoke_document_creation,
            )
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_new_or_unification_without_unifier,
            )
            # Unification
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_unification,
                predicate=DocumentProcessingSagaData.is_invoke_unifier,
            )
            .on_reply(PerformUnificationReply, Handlers.evaluate_error_from_reply)
            .on_reply(
                PerformContainerUnificationReply,
                Handlers.evaluate_container_unification_result,
            )
            # Update container document
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_container_data,
                predicate=DocumentProcessingSagaData.is_container_type,
            )
            .on_reply(UpdateContainerDataReply, Handlers.evaluate_error_from_reply)
            # Start attachment processing
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.start_attachments_processing,
                predicate=DocumentProcessingSagaData.is_attachment_processing_possible,
            )
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_unifier,
            )
            # Image preprocessing
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_image_preprocessing,
                predicate=DocumentProcessingSagaData.is_invoke_image_preprocessing,
            )
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_image_preprocessing,
            )
            # Parsing
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_parsing,
                predicate=DocumentProcessingSagaData.is_invoke_parsing,
            )
            .on_reply(PerformParsingReply, Handlers.evaluate_error_from_reply)
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_parsing_completion,
            )
            # Version Classification
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_version_classification,
                predicate=DocumentProcessingSagaData.is_invoke_version_classification,
            )
            .on_reply(
                PerformVersionClassificationReply,
                Handlers.evaluate_version_classification_result,
            )
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_version_classification,
            )
            # Extraction
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_extraction,
                predicate=DocumentProcessingSagaData.is_invoke_extraction,
            )
            .on_reply(PerformExtractionReply, Handlers.evaluate_error_from_reply)
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_extraction,
            )
            # Postprocessing
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_postprocessing,
                predicate=DocumentProcessingSagaData.is_invoke_postprocessing,
            )
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_postprocessing,
            )
            # Validation
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_validation,
                predicate=DocumentProcessingSagaData.is_invoke_validation,
            )
            .on_reply(PerformValidationReply, Handlers.save_validation_result)
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_validation,
            )
            # Exporting
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.perform_output_exporting,
                predicate=DocumentProcessingSagaData.is_invoke_output_exporting,
            )
            .on_reply(PerformExportingReply, Handlers.evaluate_error_from_reply)
            .step()
            .invoke_participant(
                DocumentProcessingSagaData.update_state,
                predicate=DocumentProcessingSagaData.is_invoke_output_exporting,
            )
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: DocumentProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is completed successfully", saga_id, data.document_id)

    def on_saga_failed(self, saga_id: str, data: DocumentProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is failed", saga_id, data.document_id)

    def on_saga_rolled_back(self, saga_id: str, data: DocumentProcessingSagaData) -> None:
        self._logger.info("Saga: %s for document: %s is rolled back", saga_id, data.document_id)
