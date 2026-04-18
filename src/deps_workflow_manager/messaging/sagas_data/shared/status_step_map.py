from deps_workflow_manager.domain.model import DocumentState, Status

__all__ = ["DocumentStatusStateMap"]


class DocumentStatusStateMap:
    _state_status_map = {
        DocumentState.NEW: Status.NEW,
        DocumentState.UNIFICATION: Status.UNIFICATION,
        DocumentState.IDENTIFICATION: Status.CLASSIFICATION,
        DocumentState.IMAGE_PREPROCESSING: Status.IMAGE_PREPROCESSING,
        DocumentState.PARSING: Status.PARSING,
        DocumentState.VERSION_IDENTIFICATION: Status.VERSION_CLASSIFICATION,
        DocumentState.DATA_EXTRACTION: Status.EXTRACTION,
        DocumentState.POSTPROCESSING: Status.POSTPROCESSING,
        DocumentState.VALIDATION: Status.VALIDATION,
        DocumentState.NEEDS_REVIEW: Status.NEEDS_REVIEW,
        DocumentState.EXPORTING: Status.EXPORTING,
        DocumentState.EXPORTED: Status.EXPORTED,
        DocumentState.FAILED: Status.FAILURE,
        DocumentState.EXCEPTIONAL_QUEUE: Status.EXCEPTIONAL_QUEUE,
        DocumentState.POSTPONED: Status.POSTPONED,
        DocumentState.COMPLETED: Status.COMPLETED,
    }

    _status_state_map = {
        Status.NEW: DocumentState.NEW,
        Status.UNIFICATION: DocumentState.UNIFICATION,
        Status.CLASSIFICATION: DocumentState.IDENTIFICATION,
        Status.IMAGE_PREPROCESSING: DocumentState.IMAGE_PREPROCESSING,
        Status.PARSING: DocumentState.PARSING,
        Status.VERSION_CLASSIFICATION: DocumentState.VERSION_IDENTIFICATION,
        Status.EXTRACTION: DocumentState.DATA_EXTRACTION,
        Status.POSTPROCESSING: DocumentState.POSTPROCESSING,
        Status.VALIDATION: DocumentState.VALIDATION,
        Status.NEEDS_REVIEW: DocumentState.NEEDS_REVIEW,
        Status.EXPORTING: DocumentState.EXPORTING,
        Status.EXPORTED: DocumentState.EXPORTED,
        Status.FAILURE: DocumentState.FAILED,
        Status.EXCEPTIONAL_QUEUE: DocumentState.EXCEPTIONAL_QUEUE,
        Status.POSTPONED: DocumentState.POSTPONED,
        Status.COMPLETED: DocumentState.COMPLETED,
    }

    @classmethod
    def status_from_state(cls, state: DocumentState) -> Status:
        if status := cls._state_status_map.get(state):
            return status
        raise RuntimeError(f"Document status for state {state} is not defined.")

    @classmethod
    def state_from_status(cls, status: Status) -> DocumentState:
        if state := cls._status_state_map.get(status):
            return state
        raise RuntimeError(f"Document state for status {status} is not defined.")
