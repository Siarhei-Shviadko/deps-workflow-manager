from deps_workflow_manager.domain.model import DocumentState

from ..document_processing_state_machine import DocumentProcessingStateMachine

__all__ = ["TemplateProcessingStateMachine"]


class TemplateProcessingStateMachine(DocumentProcessingStateMachine):
    DOCUMENT_STATES_ORDER = [
        DocumentState.NEW,
        DocumentState.PREPROCESSING,
        DocumentState.IDENTIFICATION,
        DocumentState.DATA_EXTRACTION,
        DocumentState.VALIDATION,
        DocumentState.COMPLETED,
    ]

    def __init__(
        self,
        current_state: DocumentState = DocumentState.NEW,
        next_state: DocumentState = DocumentState.NEW,
        invoke_unifier: bool = True,
        invoke_preprocessor: bool = True,
        invoke_version_classification: bool = False,
        invoke_extraction: bool = True,
        invoke_validation: bool = False,
    ):
        super().__init__(current_state=current_state, next_state=next_state)

        self._invoke_unifier = invoke_unifier
        self._invoke_preprocessor = invoke_preprocessor
        self._invoke_version_classification = invoke_version_classification
        self._invoke_extraction = invoke_extraction
        self._invoke_validation = invoke_validation

        self._fix_next_state()

    def _next_state_is_wrong(self) -> bool:
        return (
            self._need_to_skip_preprocessing()
            or self._need_to_skip_version_classification()
            or self._need_to_skip_data_extraction()
            or self._need_to_skip_validation()
        )

    def _need_to_skip_preprocessing(self) -> bool:
        return self._next_state == DocumentState.PREPROCESSING and not (
            self._invoke_unifier or self._invoke_preprocessor
        )

    def _need_to_skip_version_classification(self) -> bool:
        return self._next_state == DocumentState.IDENTIFICATION and not self._invoke_version_classification

    def _need_to_skip_data_extraction(self) -> bool:
        return self._next_state == DocumentState.DATA_EXTRACTION and not self._invoke_extraction

    def _need_to_skip_validation(self) -> bool:
        return self._next_state == DocumentState.VALIDATION and not (
            self._invoke_extraction and self._invoke_validation
        )
