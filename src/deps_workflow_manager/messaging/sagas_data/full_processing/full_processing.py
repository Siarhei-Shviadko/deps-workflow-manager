import logging
from typing import Any, Dict, List, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)

from deps_workflow_manager.domain.constants import DEFAULT_OCR_ENGINE
from deps_workflow_manager.domain.model import (
    DocumentState,
    Error,
    ErrorType,
    ExtractionType,
    ParsingFeature,
    Status,
    StepStateMachine,
    WorkflowConfiguration,
)

from ...commands import (  # noqa: WPS235
    CreateDocument,
    PerformClassification,
    PerformExtraction,
    PerformParsing,
    PerformPostprocessing,
    PerformPreprocess,
    PerformTemplateExtraction,
    PerformUnification,
    PerformValidation,
    UpdateDocumentState,
)
from ..shared import Destination

__all__ = ["FullProcessingSagaData"]


class FullProcessingSagaData:  # noqa: WPS230
    def __init__(
        self,
        document_name: str,
        tenant_id: str,
        document_type_id: Optional[str],
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        parsing_features: Optional[set[ParsingFeature]],
        files: List[str],
        assign_to_me: bool,
        *,
        document_id: Optional[str] = None,
        current_status: Status = Status.NEW,
        image_transformations: Optional[set[str]] = None,
        extraction_type: Optional[ExtractionType] = None,
        invoke_unifier: bool = True,
        invoke_classification: bool = False,
        invoke_image_preprocessing: bool = False,
        invoke_extraction: bool = True,
        invoke_postprocessing: bool = False,
        invoke_validation: bool = False,
        error: Optional[Error] = None,
        needs_exceptional_queue: bool = False,
        needs_user_verification: bool = False,
        validation_result: Optional[bool] = None,
        document_metadata: Optional[dict] = None,
    ) -> None:
        self.document_name = document_name
        self.tenant_id = tenant_id
        self.document_type_id = document_type_id
        self.engine = engine
        self.language = language
        self.parsing_features = parsing_features
        self.files = files
        self.assign_to_me = assign_to_me

        self.document_id = document_id
        self.current_status = current_status
        self.image_transformations = image_transformations
        self.extraction_type = extraction_type
        self.llm_type = llm_type

        self.invoke_unifier = invoke_unifier
        self.invoke_classification = invoke_classification
        self.invoke_image_preprocessing = invoke_image_preprocessing
        self.invoke_extraction = invoke_extraction
        self.invoke_postprocessing = invoke_postprocessing
        self.invoke_validation = invoke_validation

        self.needs_exceptional_queue = needs_exceptional_queue
        self.needs_user_verification = needs_user_verification

        self.validation_result = validation_result

        self.document_metadata = document_metadata

        self._step_state_machine = StepStateMachine(
            current_status=current_status,
            document_type=self.document_type_id,
            needs_unification=self.invoke_unifier,
            classification_enabled=self.invoke_classification,
            needs_image_preprocessing=self.invoke_image_preprocessing,
            needs_parsing=self.invoke_parsing,
            needs_extraction=self.invoke_extraction,
            needs_postprocessing=self.invoke_postprocessing,
            needs_validation=self.invoke_validation,
            error=error,
            needs_exceptional_queue=self.needs_exceptional_queue,
            needs_user_verification=self.needs_user_verification,
        )

        self._step = self._step_state_machine.current_step

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def error(self) -> Error:
        return self._step.error

    @error.setter
    def error(self, error: Error) -> None:
        self._step.error = error
        self._step_state_machine.error = error

    @property
    def invoke_parsing(self) -> bool:
        return bool(self.parsing_features)

    def is_invoke_document_creation(self) -> bool:
        return self._step.status == Status.NEW

    def is_invoke_unifier(self) -> bool:
        return self.invoke_unifier and self._step.status == Status.UNIFICATION

    def is_invoke_classification(self) -> bool:
        return self.invoke_classification and self._step.status == Status.CLASSIFICATION

    def is_invoke_image_preprocessing(self) -> bool:
        return self.invoke_image_preprocessing and self._step.status == Status.IMAGE_PREPROCESSING

    def is_invoke_extraction(self) -> bool:
        return self.invoke_extraction and self._step.status == Status.EXTRACTION and self.extraction_type

    def is_invoke_postprocessing(self) -> bool:
        return self.invoke_postprocessing and self._step.status == Status.POSTPROCESSING

    def is_invoke_validation(self) -> bool:
        return self.invoke_validation and self._step.status == Status.VALIDATION

    def is_invoke_parsing(self) -> bool:
        return self.invoke_parsing and self._step.status == Status.PARSING

    def create_document(self) -> CommandWithDestination:
        self._logger.info(
            f"Creating document with "
            f"document_name={self.document_name}, "
            f"document_type_id={self.document_type_id}, "
            f"engine={self.document_type_id}, "
            f"language={self.document_type_id}, "
            f"llm_type={self.document_type_id}",
        )
        return (
            CommandWithDestinationBuilder.send(
                CreateDocument(
                    self.document_name,
                    self.document_type_id,
                    self.engine,
                    self.language,
                    self.llm_type,
                    self.files,
                    self.assign_to_me,
                    self.document_metadata,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def update_state(self) -> CommandWithDestination:
        self._step = self._step_state_machine.next_step
        self.current_status = self._step.status

        document_state = self._get_document_state(self._step.status)
        self._logger.info(f"Updating document {self.document_id} state to: {document_state}")

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(document_id=self.document_id, state=document_state, error=self.error),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def perform_unification(self) -> CommandWithDestination:
        self._logger.info(f"Sending document {self.document_id} to unification")

        if self.document_id is None:
            raise RuntimeError("Could not send perform unification command. Document id is not defined.")

        return (
            CommandWithDestinationBuilder.send(PerformUnification(self.document_id, self.document_type_id, self.files))
            .to(Destination.UNIFIER_SERVICE)
            .build()
        )

    def perform_classification(self) -> CommandWithDestination:
        self._logger.info(f"Sending document {self.document_id} to classification")
        return (
            CommandWithDestinationBuilder.send(PerformClassification(self.document_id))
            .to(Destination.CLASSIFICATION_SERVICE)
            .build()
        )

    def perform_image_preprocessing(self) -> CommandWithDestination:
        image_transformations = list(self.image_transformations) if self.image_transformations else None
        self._logger.info(f"Sending document {self.document_id} to image preprocessing with {image_transformations=}")
        return (
            CommandWithDestinationBuilder.send(
                PerformPreprocess(document_id=self.document_id, image_transformations=image_transformations),
            )
            .to(Destination.IMAGE_PREPROCESS_SERVICE)
            .build()
        )

    def perform_extraction(self) -> CommandWithDestination:
        if self.document_id is None or self.document_type_id is None:
            raise RuntimeError(
                "Could not send perform extraction command. Document id or document type id is not defined.",
            )
        return self._get_extraction_command()

    def perform_postprocessing(self) -> CommandWithDestination:
        self._logger.info(f"Sending document {self.document_id} to postprocessing")
        return (
            CommandWithDestinationBuilder.send(
                PerformPostprocessing(
                    self.document_id,
                ),
            )
            .to(Destination.POSTPROCESSING_SERVICE)
            .build()
        )

    def perform_validation(self) -> CommandWithDestination:
        self._logger.info(f"Sending document {self.document_id} to validation")
        return (
            CommandWithDestinationBuilder.send(
                PerformValidation(
                    self.document_id,
                    self.document_type_id,
                ),
            )
            .to(Destination.VALIDATION_SERVICE)
            .build()
        )

    def set_workflow_configuration(self, configuration: Optional[WorkflowConfiguration]) -> None:
        self._logger.info(
            f"Setting processing configuration for document {self.document_id} with type {self.document_type_id}",
        )
        if configuration is None:
            self.error = Error(ErrorType.SYSTEM, "There is no workflow config for the document type.")
            return

        if self.invoke_extraction and configuration.extraction_type is None:
            self.error = Error(ErrorType.SYSTEM, "There is no extraction capability for the document type.")
            return

        self.image_transformations = configuration.image_transformations
        self.extraction_type = configuration.extraction_type

        self.invoke_image_preprocessing = configuration.needs_image_preprocessing
        self.invoke_postprocessing = configuration.needs_postprocessing
        self.invoke_validation = configuration.needs_validation
        self.parsing_features = self.parsing_features or configuration.parsing_features
        self.llm_type = self.llm_type or configuration.llm_type
        self.needs_user_verification = configuration.needs_user_verification

        self._logger.debug(
            f"Configuration for document {self.document_id}: "
            f"image_transformations={self.image_transformations}, "
            f"extraction_type={self.extraction_type}, "
            f"invoke_image_preprocessing={self.invoke_image_preprocessing}, "
            f"invoke_postprocessing={self.invoke_postprocessing}, "
            f"invoke_validation={self.invoke_validation}, "
            f"parsing_features={self.parsing_features}, "
            f"llm_type={self.llm_type}, "
            f"needs_user_verification={self.needs_user_verification}",
        )

        self._step_state_machine.update(
            needs_image_preprocessing=self.invoke_image_preprocessing,
            needs_parsing=self.invoke_parsing,
            needs_postprocessing=self.invoke_postprocessing,
            needs_validation=self.invoke_validation,
            needs_user_verification=self.needs_user_verification,
        )

        self._step = self._step_state_machine.current_step

    def perform_parsing(self) -> CommandWithDestination:
        engine = self.engine or DEFAULT_OCR_ENGINE
        parsing_features = list(self.parsing_features) if self.parsing_features else None
        self._logger.info(f"Sending document {self.document_id} to parsing with {engine=} and {parsing_features=}")
        return (
            CommandWithDestinationBuilder.send(
                PerformParsing(
                    tenant_id=self.tenant_id,
                    document_id=self.document_id,
                    files=self.files,
                    document_type_id=self.document_type_id,
                    engine=engine,
                    features=parsing_features,
                    language=self.language,
                ),
            )
            .to(Destination.PARSING_SERVICE)
            .build()
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_name": self.document_name,
            "tenant_id": self.tenant_id,
            "document_type_id": self.document_type_id,
            "engine": self.engine,
            "language": self.language,
            "llm_type": self.llm_type,
            "parsing_features": list(self.parsing_features) if self.parsing_features else None,
            "files": self.files,
            "assign_to_me": self.assign_to_me,
            "document_id": self.document_id,
            "current_status": self.current_status.value,
            "invoke_unifier": self.invoke_unifier,
            "invoke_classification": self.invoke_classification,
            "invoke_image_preprocessing": self.invoke_image_preprocessing,
            "invoke_extraction": self.invoke_extraction,
            "invoke_postprocessing": self.invoke_postprocessing,
            "invoke_validation": self.invoke_validation,
            "error_type": self._step.error.type.value if self._step.error is not None else None,
            "error_message": self._step.error.message if self._step.error is not None else None,
            "needs_exceptional_queue": self.needs_exceptional_queue,
            "needs_user_verification": self.needs_user_verification,
            "validation_result": self.validation_result,
            "extraction_type": self.extraction_type,
            "document_metadata": self.document_metadata,
        }

    @classmethod
    def from_dict(cls, raw_data: Dict[str, Any]) -> "FullProcessingSagaData":
        return cls(
            raw_data["document_name"],
            raw_data["tenant_id"],
            raw_data["document_type_id"],
            raw_data["engine"],
            raw_data["language"],
            raw_data["llm_type"],
            {ParsingFeature(feature) for feature in raw_data["parsing_features"]}
            if raw_data["parsing_features"]
            else None,
            raw_data["files"],
            raw_data["assign_to_me"],
            document_id=raw_data["document_id"],
            current_status=Status(raw_data["current_status"]),
            invoke_unifier=raw_data["invoke_unifier"],
            invoke_classification=raw_data["invoke_classification"],
            invoke_image_preprocessing=raw_data["invoke_image_preprocessing"],
            invoke_extraction=raw_data["invoke_extraction"],
            invoke_postprocessing=raw_data["invoke_postprocessing"],
            invoke_validation=raw_data["invoke_validation"],
            error=Error(ErrorType(raw_data["error_type"]), raw_data["error_message"])
            if raw_data["error_type"] is not None and raw_data["error_message"] is not None
            else None,
            needs_exceptional_queue=raw_data["needs_exceptional_queue"],
            needs_user_verification=raw_data["needs_user_verification"],
            validation_result=raw_data["validation_result"],
            extraction_type=raw_data["extraction_type"],
            document_metadata=raw_data["document_metadata"],
        )

    def _get_document_state(self, status: Status) -> DocumentState:
        mapping = {
            Status.NEW: DocumentState.NEW,
            Status.UNIFICATION: DocumentState.UNIFICATION,
            Status.CLASSIFICATION: DocumentState.IDENTIFICATION,
            Status.IMAGE_PREPROCESSING: DocumentState.IMAGE_PREPROCESSING,
            Status.PARSING: DocumentState.PARSING,
            Status.EXTRACTION: DocumentState.DATA_EXTRACTION,
            Status.POSTPROCESSING: DocumentState.POSTPROCESSING,
            Status.VALIDATION: DocumentState.VALIDATION,
            Status.NEEDS_REVIEW: DocumentState.NEEDS_REVIEW,
            Status.FAILURE: DocumentState.FAILED,
            Status.EXCEPTIONAL_QUEUE: DocumentState.EXCEPTIONAL_QUEUE,
            Status.POSTPONED: DocumentState.POSTPONED,
            Status.COMPLETED: DocumentState.COMPLETED,
        }

        if status not in mapping:
            raise RuntimeError(f"Document state for status {status} is not defined.")

        return mapping[status]

    def _perform_plugin_extraction(self) -> CommandWithDestination:
        self._logger.info(
            f"Sending document {self.document_id} with type {self.document_type_id} to plugin extraction",
        )
        return (
            CommandWithDestinationBuilder.send(
                PerformExtraction(
                    tenant_id=self.tenant_id,
                    document_id=self.document_id,
                    document_type_id=self.document_type_id,
                    language=self.language,
                    engine=self.engine,
                    llm_type=self.llm_type,
                ),
            )
            .to(Destination.EXTRACTION_SERVICE)
            .build()
        )

    def _perform_template_extraction(self) -> CommandWithDestination:
        self._logger.info(
            f"Sending document {self.document_id} with type {self.document_type_id} to template extraction",
        )
        return (
            CommandWithDestinationBuilder.send(
                PerformTemplateExtraction(
                    template_id=self.document_type_id,
                    tenant_id=self.tenant_id,
                    document_id=int(self.document_id),
                    language=self.language,
                    engine=self.engine,
                ),
            )
            .to(Destination.TEMPLATE_SERVICE)
            .build()
        )

    def _get_extraction_command(self) -> CommandWithDestination:
        mapper = {
            ExtractionType.TEMPLATE: self._perform_template_extraction,
            ExtractionType.PLUGIN: self._perform_plugin_extraction,
        }

        if self.extraction_type not in mapper:
            raise RuntimeError(f"Extraction command for extraction type {self.extraction_type} is not defined.")

        return mapper[self.extraction_type]()
