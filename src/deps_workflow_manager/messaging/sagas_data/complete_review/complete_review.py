import logging
from typing import Any, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from deps_workflow_manager.constants import (
    DOCUMENT_SERVICE_CHANNEL,
    VALIDATION_SERVICE_CHANNEL,
)
from deps_workflow_manager.domain.model import DocumentState

from ...commands import PerformValidation, UnassignReviewer, UpdateDocumentState

logger = logging.getLogger(__name__)


__all__ = ["CompleteReviewSagaData"]


class CompleteReviewSagaData(SagaData):  # noqa: WPS230
    def __init__(
        self,
        document_type_id: str,
        document_id: str,
        metadata: dict[str, Any],
        current_state: DocumentState = DocumentState.IN_REVIEW,
        next_state: DocumentState = DocumentState.IN_REVIEW,
        validation_failed_next_step: DocumentState = DocumentState.IN_REVIEW,
        validation_result: Optional[bool] = None,
    ) -> None:
        super().__init__(entity_id=document_id)
        self.document_type_id = document_type_id
        self.metadata = metadata
        self.validation_result = validation_result

        self.current_state = current_state
        self.next_state = next_state
        self.validation_failed_next_step = validation_failed_next_step

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def document_id(self) -> str:
        return self.entity_id

    def perform_validation(self) -> CommandWithDestination:
        self._logger.info(f"Performing validation for document {self.document_id}")
        self.update_next_state(DocumentState.COMPLETED)
        return (
            CommandWithDestinationBuilder.send(
                PerformValidation(document_id=self.document_id, document_type_id=self.document_type_id),
            )
            .to(VALIDATION_SERVICE_CHANNEL)
            .build()
        )

    def unassign_reviewer(self) -> CommandWithDestination:
        self._logger.info(f"Unassigning reviewer for document {self.document_id}")
        return (
            CommandWithDestinationBuilder.send(
                UnassignReviewer(document_id=self.document_id),
            )
            .to(DOCUMENT_SERVICE_CHANNEL)
            .build()
        )

    def should_unassign_reviewer(self) -> bool:
        return self.next_state == DocumentState.COMPLETED

    def is_invoke_state_update(self) -> bool:
        return self.current_state != self.next_state

    def update_current_state(self) -> None:
        self._logger.info(f"Updating document {self.document_id} state to: {self.next_state}")
        self.current_state = self.next_state

    def update_next_state(self, state: DocumentState) -> None:
        self.next_state = state

    def update_state(self) -> CommandWithDestination:
        self.update_current_state()

        return (
            CommandWithDestinationBuilder.send(
                UpdateDocumentState(
                    self.document_id,
                    self.current_state,
                ),
            )
            .to(DOCUMENT_SERVICE_CHANNEL)
            .build()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "document_type_id": self.document_type_id,
            "validation_result": self.validation_result,
            "current_state": self.current_state,
            "next_state": self.next_state,
            "validation_failed_next_step": self.validation_failed_next_step,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "CompleteReviewSagaData":
        return cls(
            document_id=raw_data["entity_id"],
            document_type_id=raw_data["document_type_id"],
            validation_result=raw_data["validation_result"],
            current_state=raw_data["current_state"],
            next_state=raw_data["next_state"],
            validation_failed_next_step=raw_data["validation_failed_next_step"],
            metadata=raw_data["metadata"],
        )
