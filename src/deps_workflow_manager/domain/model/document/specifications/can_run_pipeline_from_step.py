from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.interfaces import IDocumentSpecification

from ..entity import Document
from ..state import PROCESSING_STATES, DocumentState

__all__ = ["CanRunPipelineFromStepSpecification"]


class CanRunPipelineFromStepSpecification(IDocumentSpecification):
    def __init__(self, documents: list[Document]) -> None:
        self._documents = documents

    def check(self) -> None:
        for document in self._documents:
            if not self.is_satisfied_by(document):
                raise WorkflowManagerException(
                    f"Document with id {document.id} has incorrect state - {document.state}. "
                    + "Documents must not be in one of these states - "
                    + f"{', '.join(((DocumentState.NEW,) + PROCESSING_STATES))}.",
                )

    @staticmethod
    def is_satisfied_by(document: Document) -> bool:
        return document.state not in PROCESSING_STATES and document.state != DocumentState.NEW
