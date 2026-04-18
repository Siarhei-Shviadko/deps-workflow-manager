from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.interfaces import IDocumentSpecification
from deps_workflow_manager.domain.model import PROCESSING_STATES, Document

__all__ = ["CanRetryLastStepSpecification"]


class CanRetryLastStepSpecification(IDocumentSpecification):
    def __init__(self, document: Document) -> None:
        self._document = document

    def check(self) -> None:
        if not self.is_satisfied_by(self._document):
            raise WorkflowManagerException(
                f"Cannot retry last step for document with id {self._document.id}. "
                + f"Document has incorrect error state - {self._document.error_in_state}. ",
            )

    @staticmethod
    def is_satisfied_by(document: Document) -> bool:
        return document.error_in_state in PROCESSING_STATES
