import logging
from typing import Any, Dict, List, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)

from deps_workflow_manager.domain.constants import DEFAULT_OCR_ENGINE
from deps_workflow_manager.domain.model import (
    ContainerData,
    DocumentProcessingInfo,
    Error,
    ErrorType,
    ExtractionType,
    ParsingFeature,
    PipelineStateMachine,
    Status,
    WorkflowConfiguration,
)

from ...commands import (
    CreateDocument,
    PerformExporting,
    PerformExtraction,
    PerformParsing,
    PerformPostprocessing,
    PerformPreprocess,
    PerformUnification,
    PerformValidation,
    PerformVersionClassification,
    StartAttachmentsProcessing,
    UpdateContainerData,
    UpdateDocumentState,
)
from ..shared import Destination, DocumentStatusStateMap

__all__ = ["DocumentProcessingSagaData"]


class DocumentProcessingSagaData:  # noqa: WPS230
    def __init__(
        self,
        document_name: Optional[str],
        tenant_id: str,
        document_type_id: str,
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        parsing_features: Optional[set[ParsingFeature]],
        output_profile_ids: Optional[list[str]],
        files: List[str],
        assign_to_me: bool,
        *,
        document_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        container_data: Optional[ContainerData] = None,
        current_status: Status = Status.NEW,
        template_version_id: Optional[str] = None,
        image_transformations: Optional[set[str]] = None,
        extraction_type: Optional[ExtractionType] = None,
        needs_unifier: bool = True,
        needs_image_preprocessing: bool = False,
        needs_extraction: bool = True,
        needs_postprocessing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_user_verification: Optional[bool] = None,
        needs_output_exporting: Optional[bool] = None,
        needs_review_on_validation_failure: Optional[bool] = None,
        needs_parsing: Optional[bool] = None,
        exceptional_queue_enabled: bool = False,
        version_classification_enabled: bool = False,
        validation_result: Optional[bool] = None,
        document_metadata: Optional[dict] = None,
        error: Optional[Error] = None,
    ) -> None:
        self.document_name = document_name
        self.tenant_id = tenant_id
        self.document_type_id = document_type_id
        self.parent_id = parent_id
        self.engine = engine
        self.language = language
        self.llm_type = llm_type
        self.parsing_features = parsing_features
        self.output_profile_ids = output_profile_ids
        self.files = files
        self.assign_to_me = assign_to_me
        self.template_version_id = template_version_id

        self.document_id = document_id
        self.current_status = current_status
        self.image_transformations = image_transformations
        self.extraction_type = extraction_type

        self.needs_unifier = needs_unifier
        self.needs_image_preprocessing = needs_image_preprocessing
        self.needs_extraction = needs_extraction
        self.needs_postprocessing = needs_postprocessing
        self.needs_validation = needs_validation and needs_extraction
        self.needs_user_verification = needs_user_verification
        self.needs_output_exporting = needs_output_exporting
        self.needs_review_on_validation_failure = needs_review_on_validation_failure
        self.needs_parsing = needs_parsing

        self.version_classification_enabled = version_classification_enabled
        self.exceptional_queue_enabled = exceptional_queue_enabled

        self.validation_result = validation_result
        self.document_metadata = document_metadata

        self._step_state_machine = PipelineStateMachine(
            current_status=current_status,
            document_type_id=self.document_type_id,
            container_type=container_data.type if container_data else None,
            exceptional_queue_enabled=self.exceptional_queue_enabled,
            error=error,
            **{param: value for param, value in self.processing_params.items() if value is not None},
        )

        self._step = self._step_state_machine.current_step
        self.container_data = container_data

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def processing_params(self) -> dict[str, Optional[bool]]:
        return {
            "needs_unification": self.needs_unifier,
            "needs_image_preprocessing": self.needs_image_preprocessing,
            "needs_parsing": self.needs_parsing,
            "needs_extraction": self.needs_extraction,
            "needs_postprocessing": self.needs_postprocessing,
            "needs_validation": self.needs_validation,
            "needs_user_verification": self.needs_user_verification,
            "needs_output_exporting": self.needs_output_exporting,
            "needs_review_on_validation_failure": self.needs_review_on_validation_failure,
            "needs_version_classification": self.version_classification_enabled
            and self.extraction_type == ExtractionType.TEMPLATE,
        }

    @property
    def error(self) -> Optional[Error]:
        return self._step.error

    @error.setter
    def error(self, error: Error) -> None:
        self._step.error = error
        self._step_state_machine.error = error

    @property
    def container_data(self) -> Optional[ContainerData]:
        return self._container_data

    @container_data.setter
    def container_data(self, data: Optional[ContainerData]) -> None:
        self._container_data = data
        if data is not None:
            self.parent_id = self.document_id
            self._step_state_machine.container_type = data.type

    @property
    def document_processing_info(self) -> DocumentProcessingInfo:
        return self._get_processing_info()

    def is_invoke_document_creation(self) -> bool:
        return self._step.status == Status.NEW

    def is_not_invoke_document_creation(self) -> bool:
        return not self.is_invoke_document_creation()

    def is_invoke_unifier(self) -> bool:
        return self.needs_unifier and self._step.status == Status.UNIFICATION

    def is_invoke_without_unifier(self) -> bool:
        return not self.needs_unifier and self._step.status == Status.UNIFICATION

    def is_new_or_unification_without_unifier(self) -> bool:
        return self.is_invoke_document_creation() or self.is_invoke_without_unifier()

    def is_invoke_version_classification(self) -> bool:
        return self.version_classification_enabled and self._step.status == Status.VERSION_CLASSIFICATION

    def is_invoke_image_preprocessing(self) -> bool:
        return self.needs_image_preprocessing and self._step.status == Status.IMAGE_PREPROCESSING

    def is_invoke_extraction(self) -> bool:
        return self.needs_extraction and self._step.status == Status.EXTRACTION

    def is_invoke_postprocessing(self) -> bool:
        return self.needs_postprocessing and self._step.status == Status.POSTPROCESSING

    def is_invoke_validation(self) -> bool:
        return self.needs_validation and self._step.status == Status.VALIDATION

    def is_invoke_parsing(self) -> bool:
        return self.needs_parsing and self._step.status == Status.PARSING

    def is_invoke_parsing_completion(self) -> bool:
        return (self.needs_parsing or not self.parsing_features) and self._step.status == Status.PARSING

    def is_invoke_user_verification(self) -> bool:
        return self.needs_user_verification and self._step.status == Status.NEEDS_REVIEW

    def is_invoke_output_exporting(self) -> bool:
        return bool(self.needs_output_exporting or self.output_profile_ids) and self._step.status == Status.EXPORTING

    def is_container_type(self) -> bool:
        return self.container_data is not None

    def is_attachment_processing_possible(self) -> bool:
        return self.is_container_type() and bool(self.container_data.attachments) and not self.error

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
                    document_name=self.document_name,
                    document_type_id=self.document_type_id,
                    engine=self.engine,
                    language=self.language,
                    llm_type=self.llm_type,
                    files=self.files,
                    assign_to_me=self.assign_to_me,
                    document_metadata=self.document_metadata,
                    parent_id=self.parent_id,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def update_state(self) -> CommandWithDestination:
        self._step = self._step_state_machine.next_step
        self.current_status = self._step.status

        document_state = DocumentStatusStateMap.state_from_status(self._step.status)
        self._logger.info(f"Updating document {self.document_id} state to: {document_state}")

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(self.document_id, document_state, self.error),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def set_state(self) -> CommandWithDestination:
        document_state = DocumentStatusStateMap.state_from_status(self._step.status)
        self._logger.info(f"Setting document {self.document_id} state to: {document_state}")
        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(self.document_id, document_state, self.error),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def update_container_data(self) -> CommandWithDestination:
        self._logger.info(f"Updating container data of document {self.document_id}")
        return (
            CommandWithDestinationBuilder.send(
                UpdateContainerData(
                    document_id=self.document_id,
                    container_type=self.container_data.type,
                    container_metadata=self.container_data.metadata,
                ),
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

    def perform_version_classification(self) -> CommandWithDestination:
        self._logger.info(
            f"Sending document {self.document_id} with type {self.document_type_id} to version classification",
        )
        return (
            CommandWithDestinationBuilder.send(
                PerformVersionClassification(
                    document_id=self.document_id,
                    files=self.files,
                    template_id=self.document_type_id,
                ),
            )
            .to(Destination.VERSION_CLASSIFICATION_SERVICE)
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
        if self.document_id is None:
            raise RuntimeError("Could not send perform extraction command. Document id is not defined.")

        extra_data = {"template_version_id": self.template_version_id}
        self._logger.info(
            f"Sending document {self.document_id} to extraction with "
            f"document_type_id={self.document_type_id}, "
            f"extra_data={extra_data}, "
            f"engine={self.engine}, "
            f"llm_type={self.llm_type}",
        )
        return (
            CommandWithDestinationBuilder.send(
                PerformExtraction(
                    tenant_id=self.tenant_id,
                    document_id=self.document_id,
                    document_type_id=self.document_type_id,
                    extra_data={"template_version_id": self.template_version_id},
                    language=self.language,
                    engine=self.engine,
                    llm_type=self.llm_type,
                ),
            )
            .to(Destination.EXTRACTION_SERVICE)
            .build()
        )

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

    def perform_output_exporting(self) -> CommandWithDestination:
        self._logger.info(f"Sending document {self.document_id} to output exporting")
        return (
            CommandWithDestinationBuilder.send(
                PerformExporting(
                    document_id=self.document_id,
                    document_type_id=self.document_type_id,
                    profile_ids=self.output_profile_ids,
                ),
            )
            .to(Destination.EXPORTING_SERVICE)
            .build()
        )

    def set_workflow_configuration(self, configuration: Optional[WorkflowConfiguration]) -> None:
        self._logger.info(
            f"Setting processing configuration for document {self.document_id} with type {self.document_type_id}",
        )
        if configuration is None:
            self.error = Error(ErrorType.SYSTEM, "There is no workflow config for the document type.")
            return

        if configuration.extraction_type is None:
            self.needs_extraction = False

        self.image_transformations = configuration.image_transformations
        self.extraction_type = configuration.extraction_type
        self.llm_type = self.llm_type if self.llm_type is not None else configuration.llm_type
        self.engine = self.engine or configuration.engine
        self.needs_image_preprocessing = configuration.needs_image_preprocessing
        self.needs_postprocessing = configuration.needs_postprocessing

        self._set_up_processsing_param("needs_validation", configuration)
        self._set_up_processsing_param("needs_user_verification", configuration)
        self._set_up_processsing_param("needs_output_exporting", configuration)

        self._set_up_processsing_param("needs_review_on_validation_failure", configuration)

        self.parsing_features = self.parsing_features or configuration.parsing_features
        # If needs_parsing wasn't set up explicitly, use the parsing features to determine if parsing is needed
        self.needs_parsing = (
            bool(self.parsing_features)
            if self.needs_parsing is None
            else self.needs_parsing and bool(self.parsing_features)
        )

        self._step_state_machine.update(
            needs_image_preprocessing=self.needs_image_preprocessing,
            needs_extraction=self.needs_extraction,
            needs_parsing=self.needs_parsing,
            needs_postprocessing=self.needs_postprocessing,
            needs_validation=self.needs_validation and self.needs_extraction,
            needs_user_verification=self.needs_user_verification,
            needs_output_exporting=self.needs_output_exporting,
            needs_review_on_validation_failure=self.needs_review_on_validation_failure,
        )

        self._logger.debug(
            f"Configuration for document {self.document_id}: "
            f"image_transformations={self.image_transformations}, "
            f"extraction_type={self.extraction_type}, "
            f"llm_type={self.llm_type}, "
            f"needs_image_preprocessing={self.needs_image_preprocessing}, "
            f"needs_extraction={self.needs_extraction}, "
            f"needs_postprocessing={self.needs_postprocessing}, "
            f"needs_validation={self.needs_validation}, "
            f"needs_user_verification={self.needs_user_verification}, "
            f"needs_output_exporting={self.needs_output_exporting}, "
            f"needs_review_on_validation_failure={self.needs_review_on_validation_failure}, "
            f"parsing_features={self.parsing_features}, "
            f"needs_parsing={self.needs_parsing}, ",
        )

        self._step = self._step_state_machine.current_step

    def perform_parsing(self) -> CommandWithDestination:
        engine = self.engine or DEFAULT_OCR_ENGINE
        parsing_features = list(self.parsing_features) if self.parsing_features else None
        self._logger.info(f"Sending document {self.document_id} to parsing with {engine=}, {parsing_features=}")
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

    def start_attachments_processing(self) -> CommandWithDestination:
        self._logger.info(f"Starting attachment processing for document {self.document_id}")
        documents = [(attach["title"], attach["blob_name"]) for attach in self.container_data.attachments]
        return (
            CommandWithDestinationBuilder.send(
                StartAttachmentsProcessing(
                    parent_id=self.parent_id,
                    tenant_id=self.tenant_id,
                    document_type_id=self.document_type_id,
                    engine=self.engine,
                    language=self.language,
                    llm_type=self.llm_type,
                    assign_to_me=self.assign_to_me,
                    parsing_features=[feature.value for feature in self.parsing_features]
                    if self.parsing_features is not None
                    else None,
                    needs_unifier=self.needs_unifier,
                    needs_extraction=self.needs_extraction,
                    documents=documents,
                ),
            )
            .to(Destination.WORKFLOW_SERVICE)
            .build()
        )

    def record_validation_result(self, result: bool) -> None:
        self.validation_result = result

        if not result:
            self.error = Error(ErrorType.VALIDATION, "Document validation failed.")

    def to_dict(self) -> Dict[str, Any]:
        def container_data_to_dict() -> dict[str, Any]:
            return {
                "type": self.container_data.type,
                "metadata": self.container_data.metadata,
                "attachments": self.container_data.attachments,
            }

        return {
            "document_name": self.document_name,
            "tenant_id": self.tenant_id,
            "document_type_id": self.document_type_id,
            "parent_id": self.parent_id,
            "engine": self.engine,
            "language": self.language,
            "llm_type": self.llm_type,
            "parsing_features": list(self.parsing_features) if self.parsing_features else None,
            "output_profile_ids": self.output_profile_ids,
            "files": self.files,
            "assign_to_me": self.assign_to_me,
            "document_id": self.document_id,
            "current_status": self.current_status.value,
            "template_version_id": self.template_version_id,
            "needs_unifier": self.needs_unifier,
            "needs_image_preprocessing": self.needs_image_preprocessing,
            "needs_extraction": self.needs_extraction,
            "needs_postprocessing": self.needs_postprocessing,
            "needs_validation": self.needs_validation,
            "needs_user_verification": self.needs_user_verification,
            "needs_output_exporting": self.needs_output_exporting,
            "needs_review_on_validation_failure": self.needs_review_on_validation_failure,
            "needs_parsing": self.needs_parsing,
            "version_classification_enabled": self.version_classification_enabled,
            "exceptional_queue_enabled": self.exceptional_queue_enabled,
            "validation_result": self.validation_result,
            "extraction_type": self.extraction_type,
            "document_metadata": self.document_metadata,
            "container_data": container_data_to_dict() if self.container_data else None,
            "error_type": self._step.error.type.value if self._step.error is not None else None,
            "error_message": self._step.error.message if self._step.error is not None else None,
        }

    @classmethod
    def from_dict(cls, raw_data: Dict[str, Any]) -> "DocumentProcessingSagaData":
        def container_data_from_dict(data: dict[str, Any]) -> ContainerData:
            return ContainerData(type_=data["type"], metadata=data["metadata"], attachments=data["attachments"])

        return cls(
            document_name=raw_data["document_name"],
            tenant_id=raw_data["tenant_id"],
            document_type_id=raw_data["document_type_id"],
            engine=raw_data["engine"],
            language=raw_data["language"],
            llm_type=raw_data["llm_type"],
            parsing_features={ParsingFeature(feature) for feature in raw_data["parsing_features"]}
            if raw_data["parsing_features"]
            else None,
            output_profile_ids=raw_data["output_profile_ids"],
            files=raw_data["files"],
            assign_to_me=raw_data["assign_to_me"],
            document_id=raw_data["document_id"],
            parent_id=raw_data["parent_id"],
            current_status=Status(raw_data["current_status"]),
            template_version_id=raw_data["template_version_id"],
            needs_unifier=raw_data["needs_unifier"],
            needs_image_preprocessing=raw_data["needs_image_preprocessing"],
            needs_extraction=raw_data["needs_extraction"],
            needs_postprocessing=raw_data["needs_postprocessing"],
            needs_validation=raw_data["needs_validation"],
            needs_user_verification=raw_data.get("needs_user_verification"),
            needs_output_exporting=raw_data["needs_output_exporting"],
            needs_review_on_validation_failure=raw_data.get("needs_review_on_validation_failure"),
            needs_parsing=raw_data["needs_parsing"],
            version_classification_enabled=raw_data["version_classification_enabled"],
            exceptional_queue_enabled=raw_data["exceptional_queue_enabled"],
            validation_result=raw_data["validation_result"],
            extraction_type=raw_data["extraction_type"],
            document_metadata=raw_data["document_metadata"],
            container_data=container_data_from_dict(raw_data["container_data"])
            if raw_data.get("container_data")
            else None,
            error=Error(ErrorType(raw_data["error_type"]), raw_data["error_message"])
            if raw_data["error_type"] is not None and raw_data["error_message"] is not None
            else None,
        )

    def _get_processing_info(self) -> DocumentProcessingInfo:
        return DocumentProcessingInfo(
            document_id=self.document_id,
            tenant_id=self.tenant_id,
            needs_unifier=self.needs_unifier,
            needs_extraction=self.needs_extraction,
            assign_to_me=self.assign_to_me,
            parsing_features=self.parsing_features,
        )

    def _set_up_processsing_param(self, param: str, configuration: WorkflowConfiguration) -> None:
        if getattr(self, param) is not None:
            return

        setattr(self, param, getattr(configuration, param))
