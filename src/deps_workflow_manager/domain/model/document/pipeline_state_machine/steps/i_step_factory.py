from typing import Optional, Protocol

from ....shared import Error
from .step import Step

__all__ = ["IStepFactory"]


class IStepFactory(Protocol):
    _error: Optional[Error]

    @property
    def error(self) -> Optional[Error]:
        return self._error

    @error.setter
    def error(self, error: Optional[Error] = None) -> None:
        self._error = error

    def make_uploading_step(self) -> Step:
        pass

    def make_unification_step(self) -> Step:
        pass

    def make_image_preprocessing_step(self) -> Step:
        pass

    def make_parsing_step(self) -> Step:
        pass

    def make_classification_step(self) -> Step:
        pass

    def make_version_classification_step(self) -> Step:
        pass

    def make_extraction_step(self) -> Step:
        pass

    def make_postprocessing_step(self) -> Step:
        pass

    def make_validation_step(self) -> Step:
        pass

    def make_manual_review_step(self) -> Step:
        pass

    def make_exporting_step(self) -> Step:
        pass

    def make_successful_exporting_step(self) -> Step:
        pass

    def make_successful_processing_step(self) -> Step:
        pass

    def make_failed_processing_step(self) -> Step:
        pass
