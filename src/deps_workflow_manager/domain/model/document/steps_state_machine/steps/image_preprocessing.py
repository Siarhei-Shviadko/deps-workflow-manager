from typing import Optional

from ....shared import Status
from .abstract_step import AbstractStep
from .istep_factory import IStepFactory
from .step import Step

__all__ = ["ImagePreprocessing"]


class ImagePreprocessing(AbstractStep):
    def __init__(
        self,
        document_type: Optional[str],
        needs_parsing: bool,
        needs_extraction: bool,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.IMAGE_PREPROCESSING

        self._document_type = document_type
        self._needs_parsing = needs_parsing
        self._needs_extraction = needs_extraction

        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<ImagePreprocessing> document_type: {self._document_type}, "
            f"needs_parsing: {self._needs_parsing}, "
            f"needs_extraction: {self._needs_extraction}"
        )

    @property
    def is_parsing_needed(self) -> bool:
        return self._needs_parsing

    @property
    def is_document_type_provided(self) -> bool:
        return self._document_type is not None

    @property
    def is_extraction_needed(self) -> bool:
        return self.is_document_type_provided and self._needs_extraction

    def next_step(self) -> Step:
        if self.is_parsing_needed:
            return self._step_factory.make_parsing_step()
        elif self.is_extraction_needed:
            return self._step_factory.make_extraction_step()

        return self._step_factory.make_successful_processing_step()
