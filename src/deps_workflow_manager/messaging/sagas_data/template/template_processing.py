import logging
from typing import Any, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from deps_workflow_manager.api import get_current_user_tenant
from deps_workflow_manager.domain.model import DocumentState
from deps_workflow_manager.messaging.commands import (
    PerformPreprocess,
    PerformTemplateExtraction,
    PerformUnification,
    PerformValidation,
    PerformVersionClassification,
    UpdateDocumentState,
)

from .template_processing_state_machine import TemplateProcessingStateMachine

__all__ = ["TemplateProcessingSagaData"]


class TemplateProcessingSagaData(SagaData):  # noqa: WPS230
    def __init__(
        self,
        document_name: str,
        document_type_id: str,
        engine: Optional[str],
        language: Optional[str],
        files: list[str],
        *,
        invoke_unifier: bool = True,
        invoke_preprocessor: bool = True,
        invoke_version_classification: bool = False,
        invoke_extraction: bool = True,
        invoke_validation: bool = False,
        assign_to_me: bool = False,
        document_id: Optional[str] = None,
        current_state: DocumentState = DocumentState.NEW,
        next_state: DocumentState = DocumentState.NEW,
        version_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        validation_result: Optional[bool] = None,
        metadata: dict[str, Any] = None,
    ) -> None:
        super().__init__(entity_id=document_id)
        self.document_name = document_name
        self.document_type_id = document_type_id
        self.engine = engine
        self.language = language
        self.files = files
        self.version_id = version_id
        self.tenant_id = tenant_id or get_current_user_tenant()

        self.invoke_unifier = invoke_unifier
        self.invoke_preprocessor = invoke_preprocessor
        self.invoke_version_classification = invoke_version_classification
        self.invoke_extraction = invoke_extraction
        self.invoke_validation = invoke_validation
        self.assign_to_me = assign_to_me
        self.validation_result = validation_result
        self.metadata = metadata

        self._state_machine = TemplateProcessingStateMachine(
            current_state=current_state,
            next_state=next_state,
            invoke_unifier=invoke_unifier,
            invoke_preprocessor=invoke_preprocessor,
            invoke_version_classification=invoke_version_classification,
            invoke_extraction=invoke_extraction,
            invoke_validation=invoke_validation,
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def document_id(self) -> Optional[str]:
        return self.entity_id

    @document_id.setter
    def document_id(self, value: Optional[str]) -> None:
        self.entity_id = value

    @property
    def current_state(self) -> DocumentState:
        return self._state_machine.current_state

    @property
    def next_state(self) -> DocumentState:
        return self._state_machine.next_state

    def is_invoke_document_creation(self) -> bool:
        return self.next_state == DocumentState.NEW

    def is_invoke_state_update(self) -> bool:
        return self.current_state != self.next_state

    def is_invoke_unifier(self) -> bool:
        return self.invoke_unifier and self.current_state == DocumentState.PREPROCESSING

    def is_invoke_preprocessor(self) -> bool:
        return self.invoke_preprocessor and self.current_state == DocumentState.PREPROCESSING

    def is_invoke_version_classification(self) -> bool:
        return self.invoke_version_classification and self.current_state == DocumentState.IDENTIFICATION

    def is_invoke_extraction(self) -> bool:
        return self.invoke_extraction and self.current_state == DocumentState.DATA_EXTRACTION

    def is_invoke_validation_state_update(self) -> bool:
        return self.invoke_validation and self.is_invoke_state_update()

    def is_invoke_validation(self) -> bool:
        return self.invoke_validation and self.current_state == DocumentState.VALIDATION

    def update_current_state(self) -> None:
        self._state_machine.update_current_state()

    def update_next_state(self) -> None:
        self._state_machine.update_next_state()

    def update_state(self) -> CommandWithDestination:
        self.update_current_state()
        self._logger.info(f"Updating document {self.document_id} state to: {self.current_state.value}")

        return (
            CommandWithDestinationBuilder.send(UpdateDocumentState(self.document_id, self.next_state.value))
            .to("DocumentService")
            .build()
        )

    def perform_unification(self) -> CommandWithDestination:
        self.update_next_state()

        if self.document_id is None:
            raise RuntimeError("Could not send perform unification command. Document id is not defined.")
        self._logger.info(f"Sending document {self.document_id} to unification")

        return (
            CommandWithDestinationBuilder.send(PerformUnification(self.document_id, self.document_type_id, self.files))
            .to("UnifierService")
            .build()
        )

    def perform_preprocessing(self) -> CommandWithDestination:
        self.update_next_state()

        if self.document_id is None:
            raise RuntimeError("Could not send perform extraction command. Document id is not defined.")
        self._logger.info(f"Sending document {self.document_id} to preprocessing")

        return (
            CommandWithDestinationBuilder.send(PerformPreprocess(document_id=self.document_id))
            .to("ImagePreprocessCommands")
            .build()
        )

    def perform_version_classification(self) -> CommandWithDestination:
        self.update_next_state()
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
            .to("TemplateClassificationCommands")
            .build()
        )

    def perform_template_extraction(self) -> CommandWithDestination:
        self.update_next_state()
        self._logger.info(f"Sending document {self.document_id} with type {self.document_type_id} to extraction")

        return (
            CommandWithDestinationBuilder.send(
                PerformTemplateExtraction(
                    template_id=self.document_type_id,
                    tenant_id=self.tenant_id,
                    document_id=int(self.document_id),
                    version_id=self.version_id,
                    language=self.language,
                    engine=self.engine,
                ),
            )
            .to("TemplateCommands")
            .build()
        )

    def perform_validation(self) -> CommandWithDestination:
        self.update_next_state()

        if self.document_id is None:
            raise RuntimeError("Could not send perform validation command. Document id is not defined.")
        self._logger.info(f"Sending document {self.document_id} to validation")

        return (
            CommandWithDestinationBuilder.send(
                PerformValidation(
                    self.document_id,
                    self.document_type_id,
                ),
            )
            .to("ValidationService")
            .build()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_name": self.document_name,
            "document_type_id": self.document_type_id,
            "engine": self.engine,
            "language": self.language,
            "files": self.files,
            "invoke_unifier": self.invoke_unifier,
            "invoke_extraction": self.invoke_extraction,
            "invoke_version_classification": self.invoke_version_classification,
            "invoke_preprocessor": self.invoke_preprocessor,
            "entity_id": self.entity_id,
            "current_state": self.current_state.value,
            "next_state": self.next_state.value,
            "version_id": self.version_id,
            "tenant_id": self.tenant_id,
            "invoke_validation": self.invoke_validation,
            "validation_result": self.validation_result,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "TemplateProcessingSagaData":
        return cls(
            document_name=raw_data["document_name"],
            document_type_id=raw_data["document_type_id"],
            engine=raw_data["engine"],
            language=raw_data["language"],
            files=raw_data["files"],
            invoke_unifier=raw_data["invoke_unifier"],
            invoke_preprocessor=raw_data["invoke_preprocessor"],
            invoke_version_classification=raw_data["invoke_version_classification"],
            invoke_extraction=raw_data["invoke_extraction"],
            document_id=raw_data["entity_id"],
            current_state=DocumentState(raw_data["current_state"]),
            next_state=DocumentState(raw_data["next_state"]),
            version_id=raw_data["version_id"],
            tenant_id=raw_data["tenant_id"],
            invoke_validation=raw_data["invoke_validation"],
            validation_result=raw_data["validation_result"],
        )
