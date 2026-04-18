from typing import Optional

from ....shared import Error, ErrorType, Status
from .abstract_step import AbstractStep
from .istep_factory import IStepFactory
from .step import Step

__all__ = ["Extraction"]

IsErrorOccurred = bool
NeedsExceptionalQueue = bool

ErrorFlags = tuple[IsErrorOccurred, ErrorType, NeedsExceptionalQueue]


class Extraction(AbstractStep):
    def __init__(
        self,
        document_type: str,
        needs_postprocessing: bool,
        needs_validation: bool,
        needs_user_verification: bool,
        error: Optional[Error] = None,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.EXTRACTION

        self._document_type = document_type
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification

        self.error = error

        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<Extraction> document_type: {self._document_type}, "
            f"needs_postprocessing: {self._needs_postprocessing}, "
            f"needs_validation: {self._needs_validation}, "
            f"needs_user_verification: {self._needs_user_verification}, "
            f"error: {self.error}"
        )

    @property
    def is_postprocessing_needed(self) -> bool:
        return self._needs_postprocessing

    @property
    def is_validation_needed(self) -> bool:
        return self._needs_validation

    @property
    def is_user_verification_needed(self) -> bool:
        return self._needs_user_verification

    def next_step(self) -> Step:
        if self.is_error_occurred:
            return self._step_factory.make_system_failed_step()
        elif self.is_postprocessing_needed:
            return self._step_factory.make_postprocessing_step()
        elif self.is_validation_needed:
            return self._step_factory.make_validation_step()
        elif self.is_user_verification_needed:
            return self._step_factory.make_manual_review_step()

        return self._step_factory.make_successful_processing_step()
