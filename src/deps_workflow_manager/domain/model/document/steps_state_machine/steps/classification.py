from typing import Optional

from ....shared import Error, Status
from .abstract_step import AbstractStep
from .istep_factory import IStepFactory
from .step import Step

__all__ = ["Classification"]


class Classification(AbstractStep):
    def __init__(
        self,
        document_type: Optional[str],
        needs_image_preprocessing: bool,
        needs_parsing: bool,
        needs_extraction: bool,
        error: Optional[Error] = None,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.CLASSIFICATION

        self._document_type = document_type
        self._needs_image_preprocessing = needs_image_preprocessing
        self._needs_parsing = needs_parsing
        self._needs_extraction = needs_extraction

        self.error = error

        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<Classification> document_type: {self._document_type}, "
            f"needs_image_preprocessing: {self._needs_image_preprocessing}, "
            f"needs_parsing: {self._needs_parsing}, "
            f"needs_extraction: {self._needs_extraction}, "
            f"error: {self.error}"
        )

    @property
    def is_document_type_provided(self) -> bool:
        return self._document_type is not None

    @property
    def is_image_preprocessing_needed(self) -> bool:
        return self._needs_image_preprocessing

    @property
    def is_extraction_needed(self) -> bool:
        return self.is_document_type_provided and self._needs_extraction

    @property
    def is_parsing_needed(self) -> bool:
        return self._needs_parsing

    def next_step(self) -> Step:  # noqa: WPS231, WPS212
        if self.is_business_error_occurred:  # noqa: WPS223
            return self._step_factory.make_business_failed_step()
        elif self.is_system_error_occurred:
            return self._step_factory.make_system_failed_step()
        elif self.is_image_preprocessing_needed:
            return self._step_factory.make_image_preprocessing_step()
        elif self.is_parsing_needed:
            return self._step_factory.make_parsing_step()
        elif self.is_extraction_needed:
            return self._step_factory.make_extraction_step()

        return self._step_factory.make_successful_processing_step()
