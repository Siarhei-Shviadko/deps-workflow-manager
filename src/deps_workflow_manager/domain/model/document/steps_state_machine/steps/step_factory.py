from typing import Optional

from ....shared import Error
from .classification import Classification
from .exceptional_queue import ExceptionalQueue
from .extraction import Extraction
from .failed_processing import FailedProcessing
from .image_preprocessing import ImagePreprocessing
from .manual_review import ManualReview
from .parsing import Parsing
from .postponed import Postponed
from .postprocessing import Postprocessing
from .step import Step
from .successful_processing import SuccessfulProcessing
from .unification import Unification
from .uploading import Uploading
from .validation import Validation

__all__ = ["StepFactory"]


class StepFactory:
    def __init__(
        self,
        document_type: Optional[str],
        needs_unification: bool = True,
        classification_enabled: bool = False,
        needs_image_preprocessing: bool = False,
        needs_parsing: bool = False,
        needs_extraction: bool = True,
        needs_postprocessing: bool = False,
        needs_validation: bool = False,
        error: Optional[Error] = None,
        needs_exceptional_queue: bool = False,
        needs_user_verification: bool = False,
    ) -> None:
        self._document_type = document_type

        self._need_unification = needs_unification
        self._classification_enabled = classification_enabled
        self._needs_image_preprocessing = needs_image_preprocessing
        self._needs_parsing = needs_parsing
        self._needs_extraction = needs_extraction
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation

        self.error = error
        self._needs_exceptional_queue = needs_exceptional_queue
        self._needs_user_verification = needs_user_verification

    def make_uploading_step(self) -> Step:
        return Uploading(self._need_unification, step_factory=self)

    def make_unification_step(self) -> Step:
        return Unification(
            document_type=self._document_type,
            classification_enabled=self._classification_enabled,
            needs_image_preprocessing=self._needs_image_preprocessing,
            needs_parsing=self._needs_parsing,
            needs_extraction=self._needs_extraction,
            error=self.error,
            step_factory=self,
        )

    def make_classification_step(self) -> Step:
        return Classification(
            document_type=self._document_type,
            needs_image_preprocessing=self._needs_image_preprocessing,
            needs_parsing=self._needs_parsing,
            needs_extraction=self._needs_extraction,
            error=self.error,
            step_factory=self,
        )

    def make_image_preprocessing_step(self) -> Step:
        return ImagePreprocessing(
            document_type=self._document_type,
            needs_parsing=self._needs_parsing,
            needs_extraction=self._needs_extraction,
            step_factory=self,
        )

    def make_parsing_step(self) -> Step:
        return Parsing(
            document_type=self._document_type,
            needs_extraction=self._needs_extraction,
            error=self.error,
            step_factory=self,
        )

    def make_extraction_step(self) -> Step:
        return Extraction(
            document_type=self._document_type,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            error=self.error,
            step_factory=self,
        )

    def make_postprocessing_step(self) -> Step:
        return Postprocessing(
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            step_factory=self,
        )

    def make_validation_step(self) -> Step:
        return Validation(
            needs_user_verification=self._needs_user_verification,
            step_factory=self,
        )

    def make_successful_processing_step(self) -> Step:
        return SuccessfulProcessing()

    def make_manual_review_step(self) -> Step:
        return ManualReview()

    def make_business_failed_step(self) -> Step:
        if self._needs_exceptional_queue:
            return ExceptionalQueue(self.error)

        return Postponed(self.error)

    def make_system_failed_step(self) -> Step:
        return FailedProcessing(self.error)
