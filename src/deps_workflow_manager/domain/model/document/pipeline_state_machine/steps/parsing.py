from typing import Optional

from ....shared import Status
from .abstract_step import AbstractStep
from .i_step_factory import IStepFactory
from .step import Step

__all__ = ["Parsing"]


class Parsing(AbstractStep):
    def __init__(
        self,
        document_type_id: Optional[str],
        needs_version_classification: bool,
        needs_extraction: bool,
        needs_postprocessing: bool,
        needs_validation: bool,
        needs_user_verification: bool,
        needs_output_exporting: bool,
        classification_enabled: bool,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.PARSING

        self._document_type_id = document_type_id

        self._needs_version_classification = needs_version_classification
        self._needs_extraction = needs_extraction
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification
        self._needs_output_exporting = needs_output_exporting

        self._classification_enabled = classification_enabled

        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__}> document_type_id: {self._document_type_id}, "
            f"needs_version_classification: {self._needs_version_classification}, "
            f"needs_extraction: {self._needs_extraction}, "
            f"needs_postprocessing: {self._needs_postprocessing}, "
            f"needs_validation: {self._needs_validation}, "
            f"needs_user_verification: {self._needs_user_verification}, "
            f"classification_enabled: {self._classification_enabled}, "
            f"error: {self.error}"
        )

    @property
    def is_document_type_provided(self) -> bool:
        return self._document_type_id is not None

    def next_step(self) -> Step:
        if self.is_error_occurred:
            return self._step_factory.make_failed_processing_step()

        if self.is_document_type_provided:
            return self._next_step_with_document_type()

        return self._next_step_without_document_type()

    def _next_step_with_document_type(self) -> Step:
        if self._needs_version_classification:
            return self._step_factory.make_version_classification_step()
        elif self._needs_extraction:
            return self._step_factory.make_extraction_step()
        elif self._needs_postprocessing:
            return self._step_factory.make_postprocessing_step()
        elif self._needs_validation:
            return self._step_factory.make_validation_step()
        elif self._needs_user_verification:
            return self._step_factory.make_manual_review_step()
        elif self._needs_output_exporting:
            return self._step_factory.make_exporting_step()

        return self._step_factory.make_successful_processing_step()

    def _next_step_without_document_type(self) -> Step:
        if self._classification_enabled:
            return self._step_factory.make_classification_step()

        return self._step_factory.make_successful_processing_step()
