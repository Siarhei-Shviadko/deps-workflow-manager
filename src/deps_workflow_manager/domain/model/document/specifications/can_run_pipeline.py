from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.interfaces import IDocumentSpecification

from ..entity import Document
from ..state import DocumentState

__all__ = ["CanRunPipelineSpecification"]


class CanRunPipelineSpecification(IDocumentSpecification):
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    def check(self) -> None:
        for document in self._documents:
            if not self.is_satisfied_by(document):
                raise WorkflowManagerException(
                    f"Document with id {document.id} has incorrect state - {document.state}. "
                    + f"All documents must not be in state {DocumentState.NEW}.",
                )

    @staticmethod
    def is_satisfied_by(document: Document) -> bool:
        return document.state == DocumentState.NEW
