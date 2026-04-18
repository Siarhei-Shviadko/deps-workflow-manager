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
    Status,
)
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    PipelineStateMachine,
)

from ...commands import (  # noqa: WPS235
    AssignDocumentType,
    CreateDocument,
    PerformClassification,
    PerformParsing,
    PerformPreprocess,
    PerformUnification,
    StartAttachmentsProcessing,
    StartDocumentProcessing,
    UpdateContainerData,
    UpdateDocumentState,
)
from ..shared import Destination, DocumentStatusStateMap

__all__ = ["TypelessDocumentProcessingSagaData"]


class TypelessDocumentProcessingSagaData:  # noqa: WPS230
    def __init__(
        self,
        document_name: Optional[str],
        tenant_id: str,
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        parsing_features: Optional[set[ParsingFeature]],
        files: List[str],
        assign_to_me: bool,
        *,
        document_id: Optional[str] = None,
        document_type_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        container_data: Optional[ContainerData] = None,
        current_status: Status = Status.NEW,
        image_transformations: Optional[set[str]] = None,
        extraction_type: Optional[ExtractionType] = None,
        needs_unifier: bool = True,
        needs_image_preprocessing: bool = False,
        needs_extraction: bool = True,
        needs_postprocessing: bool = False,
        needs_validation: bool = False,
        needs_user_verification: Optional[bool] = None,
        needs_parsing: Optional[bool] = None,
        error: Optional[Error] = None,
        validation_result: Optional[bool] = None,
        document_metadata: Optional[dict] = None,
        exceptional_queue_enabled: bool = False,
        classification_enabled: bool = False,
    ) -> None:
        self.document_name = document_name
        self.tenant_id = tenant_id
        self.parent_id = parent_id
        self.engine = engine
        self.language = language
        self.llm_type = llm_type
        self.parsing_features = parsing_features
        self.files = files
        self.assign_to_me = assign_to_me

        self.document_id = document_id
        self.current_status = current_status
        self.image_transformations = image_transformations
        self.extraction_type = extraction_type

        self.needs_unifier = needs_unifier
        self.needs_image_preprocessing = needs_image_preprocessing
        self.needs_extraction = needs_extraction
        self.needs_postprocessing = needs_postprocessing
        self.needs_validation = needs_validation
        self.needs_user_verification = needs_user_verification
        self.needs_parsing = needs_parsing or bool(parsing_features)

        self.classification_enabled = classification_enabled
        self.exceptional_queue_enabled = exceptional_queue_enabled

        self.validation_result = validation_result
        self.document_metadata = document_metadata

        self._step_state_machine = PipelineStateMachine(
            current_status=current_status,
            document_type_id=document_type_id,
            container_type=container_data.type if container_data else None,
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
            "classification_enabled": self.classification_enabled,
            "exceptional_queue_enabled": self.exceptional_queue_enabled,
        }

    @property
    def error(self) -> Optional[Error]:
        return self._step.error

    @error.setter
    def error(self, error: Error) -> None:
        self._step.error = error
        self._step_state_machine.error = error

    @property
    def document_type_id(self) -> str:
        return self._step_state_machine.document_type_id

    @document_type_id.setter
    def document_type_id(self, document_type_id: str) -> None:
        self._step_state_machine.document_type_id = document_type_id

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

    def is_invoke_classification(self) -> bool:
        return self.classification_enabled and self._step.status == Status.CLASSIFICATION

    def is_classification_successful(self) -> bool:
        return self.document_type_id is not None

    def is_invoke_image_preprocessing(self) -> bool:
        return self.needs_image_preprocessing and self._step.status == Status.IMAGE_PREPROCESSING

    def is_invoke_parsing(self) -> bool:
        return self.needs_parsing and self._step.status == Status.PARSING

    def is_invoke_parsing_completion(self) -> bool:
        return (self.needs_parsing or not self.parsing_features) and self._step.status == Status.PARSING

    def is_container_type(self) -> bool:
        return self.container_data is not None

    def is_attachment_processing_possible(self) -> bool:
        return self.is_container_type() and bool(self.container_data.attachments) and not self.error

    def is_start_document_processing_possible(self) -> bool:
        return not bool(self.error) and self.is_classification_successful()

    def create_document(self) -> CommandWithDestination:
        self._logger.info(
            f"Creating document with "
            f"document_name={self.document_name}, "
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

    def perform_unification(self) -> CommandWithDestination:
        self._logger.info(f"Sending document {self.document_id} to unification")
        if self.document_id is None:
            raise RuntimeError("Could not send perform unification command. Document id is not defined.")

        return (
            CommandWithDestinationBuilder.send(PerformUnification(self.document_id, self.document_type_id, self.files))
            .to(Destination.UNIFIER_SERVICE)
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

    def assign_document_type(self) -> CommandWithDestination:
        self._logger.info(f"Assigning type {self.document_type_id} to document {self.document_id}")
        return (
            CommandWithDestinationBuilder.send(
                AssignDocumentType(
                    document_id=self.document_id,
                    document_type_id=self.document_type_id,
                ),
            )
            .to(Destination.DOCUMENT_SERVICE)
            .build()
        )

    def start_document_processing(self) -> CommandWithDestination:
        self._logger.info(
            f"Starting document processing for document `{self.document_name}` with ID {self.document_id}"
            f"and document type ID {self.document_type_id} from step {self.current_status.value}",
        )
        return (
            CommandWithDestinationBuilder.send(
                StartDocumentProcessing(
                    document_id=self.document_id,
                    document_name=self.document_name,
                    document_type_id=self.document_type_id,
                    tenant_id=self.tenant_id,
                    engine=self.engine,
                    language=self.language,
                    llm_type=self.llm_type,
                    assign_to_me=self.assign_to_me,
                    parsing_features=[feature.value for feature in self.parsing_features]
                    if self.parsing_features is not None
                    else None,
                    needs_unifier=self.needs_unifier,
                    needs_extraction=self.needs_extraction,
                    files=self.files,
                    document_metadata=self.document_metadata,
                    from_step=self.current_status.value,
                ),
            )
            .to(Destination.WORKFLOW_SERVICE)
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
            "files": self.files,
            "assign_to_me": self.assign_to_me,
            "document_id": self.document_id,
            "current_status": self.current_status.value,
            "needs_unifier": self.needs_unifier,
            "needs_image_preprocessing": self.needs_image_preprocessing,
            "needs_extraction": self.needs_extraction,
            "needs_postprocessing": self.needs_postprocessing,
            "needs_validation": self.needs_validation,
            "needs_user_verification": self.needs_user_verification,
            "needs_parsing": self.needs_parsing,
            "classification_enabled": self.classification_enabled,
            "exceptional_queue_enabled": self.exceptional_queue_enabled,
            "validation_result": self.validation_result,
            "extraction_type": self.extraction_type,
            "document_metadata": self.document_metadata,
            "container_data": container_data_to_dict() if self.container_data else None,
            "error_type": self._step.error.type.value if self._step.error is not None else None,
            "error_message": self._step.error.message if self._step.error is not None else None,
        }

    @classmethod
    def from_dict(cls, raw_data: Dict[str, Any]) -> "TypelessDocumentProcessingSagaData":
        def conatiner_data_from_dict(data: dict[str, Any]) -> ContainerData:
            return ContainerData(type_=data["type"], metadata=data["metadata"], attachments=data["attachments"])

        return cls(
            raw_data["document_name"],
            raw_data["tenant_id"],
            raw_data["engine"],
            raw_data["language"],
            raw_data["llm_type"],
            {ParsingFeature(feature) for feature in raw_data["parsing_features"]}
            if raw_data["parsing_features"]
            else None,
            raw_data["files"],
            raw_data["assign_to_me"],
            document_type_id=raw_data["document_type_id"],
            document_id=raw_data["document_id"],
            parent_id=raw_data["parent_id"],
            current_status=Status(raw_data["current_status"]),
            needs_unifier=raw_data["needs_unifier"],
            needs_image_preprocessing=raw_data["needs_image_preprocessing"],
            needs_extraction=raw_data["needs_extraction"],
            needs_postprocessing=raw_data["needs_postprocessing"],
            needs_validation=raw_data["needs_validation"],
            needs_user_verification=raw_data["needs_user_verification"],
            needs_parsing=raw_data["needs_parsing"],
            classification_enabled=raw_data["classification_enabled"],
            exceptional_queue_enabled=raw_data["exceptional_queue_enabled"],
            validation_result=raw_data["validation_result"],
            extraction_type=raw_data["extraction_type"],
            document_metadata=raw_data["document_metadata"],
            container_data=conatiner_data_from_dict(raw_data["container_data"])
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
