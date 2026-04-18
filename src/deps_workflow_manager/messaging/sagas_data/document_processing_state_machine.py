from abc import ABC, abstractmethod

from deps_workflow_manager.domain.model import DocumentState

__all__ = ["DocumentProcessingStateMachine"]


class DocumentProcessingStateMachine(ABC):
    DOCUMENT_STATES_ORDER = [DocumentState.NEW]

    def __init__(
        self,
        current_state: DocumentState = DocumentState.NEW,
        next_state: DocumentState = DocumentState.NEW,
    ):
        self._current_state = current_state
        self._next_state = next_state

    @property
    def current_state(self) -> DocumentState:
        return self._current_state

    @property
    def next_state(self) -> DocumentState:
        return self._next_state

    def update_current_state(self) -> None:
        self._current_state = self._next_state

    def update_next_state(self) -> None:
        self._next_state = self._find_next_state(state=self._current_state)
        self._fix_next_state()

    def _fix_next_state(self) -> None:
        while self._next_state_is_wrong() and self._next_state != self.DOCUMENT_STATES_ORDER[-1]:
            self._next_state = self._find_next_state(self._next_state)

    @abstractmethod
    def _next_state_is_wrong(self) -> bool:
        pass

    @classmethod
    def _find_next_state(cls, state: DocumentState) -> DocumentState:
        try:
            index = cls.DOCUMENT_STATES_ORDER.index(state)
            next_index = index + 1 if index < len(cls.DOCUMENT_STATES_ORDER) - 1 else index

            return cls.DOCUMENT_STATES_ORDER[next_index]

        except ValueError:
            raise RuntimeError(f"Cannot find next document state for state - '{state}'")
