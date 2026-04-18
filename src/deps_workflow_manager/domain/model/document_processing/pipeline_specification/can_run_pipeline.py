from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.interfaces import IDocumentSpecification
from deps_workflow_manager.domain.model import FINISHED_STATES, Document

__all__ = ["CanRunPipelineSpecification"]


class CanRunPipelineSpecification(IDocumentSpecification):
    def __init__(self, document: Document) -> None:
        self._document = document

    def check(self) -> None:
        if not self.is_satisfied_by(self._document):
            raise WorkflowManagerException(
                f"Document with id {self._document.id} has incorrect state - {self._document.state}. "
                + "Document must be in states: "
                + ", ".join(f"{s.value}" for s in FINISHED_STATES),
            )

    @staticmethod
    def is_satisfied_by(document: Document) -> bool:
        return document.state in FINISHED_STATES
