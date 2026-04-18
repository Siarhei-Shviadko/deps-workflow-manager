from typing import Protocol

from ....shared import Error
from .step import Step

__all__ = ["IStepFactory"]


class IStepFactory(Protocol):
    error: Error

    def make_uploading_step(self) -> Step:
        pass

    def make_unification_step(self) -> Step:
        pass

    def make_classification_step(self) -> Step:
        pass

    def make_image_preprocessing_step(self) -> Step:
        pass

    def make_parsing_step(self) -> Step:
        pass

    def make_extraction_step(self) -> Step:
        pass

    def make_postprocessing_step(self) -> Step:
        pass

    def make_validation_step(self) -> Step:
        pass

    def make_successful_processing_step(self) -> Step:
        pass

    def make_manual_review_step(self) -> Step:
        pass

    def make_system_failed_step(self) -> Step:
        pass

    def make_business_failed_step(self) -> Step:
        pass
