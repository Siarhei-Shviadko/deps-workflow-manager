from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.interfaces import IDocumentSpecification

from ..entity import Document
from ..state import PROCESSING_STATES

__all__ = ["CanRetryLastStepSpecification"]


class CanRetryLastStepSpecification(IDocumentSpecification):
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    def check(self) -> None:
        for document in self._documents:
            if not self.is_satisfied_by(document):
                raise WorkflowManagerException(
                    f"Cannot retry last step for document with id {document.id}. "
                    + f"Document has incorrect error state - {document.error_in_state}. ",
                )

    @staticmethod
    def is_satisfied_by(document: Document) -> bool:
        return document.error_in_state in PROCESSING_STATES
