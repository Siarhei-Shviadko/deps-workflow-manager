import logging
from typing import Any, Dict, List, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from deps_workflow_manager.api import get_current_user_tenant
from deps_workflow_manager.domain.model import DocumentState

from ...commands import (
    PerformExtraction,
    PerformUnification,
    PerformValidation,
    UpdateDocumentState,
)
from .plugin_processing_state_machine import PluginProcessingStateMachine

__all__ = ["PluginProcessingSagaData"]


class PluginProcessingSagaData(SagaData):  # noqa: WPS230
    def __init__(
        self,
        document_name: str,
        document_type_id: str,
        engine: str,
        language: str,
        files: List[str],
        *,
        invoke_unifier: bool = True,
        invoke_extraction: bool = True,
        invoke_validation: bool = False,
        assign_to_me: bool = False,
        document_id: Optional[str] = None,
        validation_result: Optional[bool] = None,
        metadata: dict[str, Any] = None,
        llm_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
        current_state: DocumentState = DocumentState.NEW,
        next_state: DocumentState = DocumentState.NEW,
    ) -> None:
        super().__init__(entity_id=document_id)
        self.document_name = document_name
        self.document_type_id = document_type_id
        self.engine = engine
        self.language = language
        self.llm_type = llm_type
        self.files = files

        self.invoke_unifier = invoke_unifier
        self.invoke_extraction = invoke_extraction
        self.invoke_validation = invoke_validation
        self.assign_to_me = assign_to_me
        self.metadata = metadata
        self.tenant_id = tenant_id or get_current_user_tenant()

        self.validation_result = validation_result

        self._state_machine = PluginProcessingStateMachine(
            current_state=current_state,
            next_state=next_state,
            invoke_unifier=invoke_unifier,
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
            CommandWithDestinationBuilder.send(UpdateDocumentState(self.document_id, self.current_state.value))
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

    def perform_extraction(self) -> CommandWithDestination:
        self.update_next_state()

        if self.document_id is None:
            raise RuntimeError("Could not send perform extraction command. Document id is not defined.")
        self._logger.info(f"Sending document {self.document_id} with type {self.document_type_id} to extraction")

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
            .to("ExtractionService")
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_name": self.document_name,
            "document_type_id": self.document_type_id,
            "engine": self.engine,
            "language": self.language,
            "files": self.files,
            "invoke_unifier": self.invoke_unifier,
            "invoke_extraction": self.invoke_extraction,
            "invoke_validation": self.invoke_validation,
            "entity_id": self.entity_id,
            "validation_result": self.validation_result,
            "current_state": self.current_state.value,
            "next_state": self.next_state.value,
        }

    @classmethod
    def from_dict(cls, raw_data: Dict[str, Any]) -> "PluginProcessingSagaData":
        return cls(
            raw_data["document_name"],
            raw_data["document_type_id"],
            raw_data["engine"],
            raw_data["language"],
            raw_data["files"],
            invoke_unifier=raw_data["invoke_unifier"],
            invoke_extraction=raw_data["invoke_extraction"],
            invoke_validation=raw_data["invoke_validation"],
            document_id=raw_data["entity_id"],
            validation_result=raw_data["validation_result"],
            current_state=DocumentState(raw_data["current_state"]),
            next_state=DocumentState(raw_data["next_state"]),
        )
