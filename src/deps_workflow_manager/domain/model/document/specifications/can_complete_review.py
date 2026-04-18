from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.interfaces import IDocumentSpecification

from ..entity import Document
from ..state import DocumentState

__all__ = ["CanCompleteReviewSpecification"]


class CanCompleteReviewSpecification(IDocumentSpecification):
    def __init__(self, document: Document) -> None:
        self._document = document

    def check(self) -> None:
        if not self.is_satisfied_by(self._document):
            raise WorkflowManagerException(
                f"Cannot complete review for document with id {self._document.id},"
                + f"document in incorrect state: {self._document.state}. "
                + f"Document has to be in  {DocumentState.IN_REVIEW}.",
            )

    @staticmethod
    def is_satisfied_by(document: Document) -> bool:
        return document.state == DocumentState.IN_REVIEW
