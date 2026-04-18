from typing import Optional

from ....shared import Error
from .classification import Classification
from .exceptional_queue import ExceptionalQueue
from .exporting import Exporting
from .extraction import Extraction
from .failure import Failure
from .i_step_factory import IStepFactory
from .image_preprocessing import ImagePreprocessing
from .manual_review import ManualReview
from .parsing import Parsing
from .postponement import Postponement
from .postprocessing import Postprocessing
from .step import Step
from .successful_exporting import SuccessfulExporting
from .successful_processing import SuccessfulProcessing
from .unification import Unification
from .uploading import Uploading
from .validation import Validation
from .version_classification import VersionClassification

__all__ = ["StepFactory"]


class StepFactory(IStepFactory):
    def __init__(
        self,
        document_type_id: Optional[str] = None,
        container_type: Optional[str] = None,
        error: Optional[Error] = None,
        needs_unification: bool = False,
        needs_image_preprocessing: bool = False,
        needs_parsing: bool = False,
        needs_version_classification: bool = False,
        needs_extraction: bool = False,
        needs_postprocessing: bool = False,
        needs_validation: bool = False,
        needs_user_verification: bool = False,
        needs_output_exporting: bool = False,
        needs_review_on_validation_failure: bool = False,
        classification_enabled: bool = False,
        exceptional_queue_enabled: bool = False,
    ) -> None:
        self._document_type_id = document_type_id
        self._container_type = container_type
        self._error = error

        self._needs_unification = needs_unification
        self._needs_image_preprocessing = needs_image_preprocessing
        self._needs_parsing = needs_parsing
        self._needs_version_classification = needs_version_classification
        self._needs_extraction = needs_extraction
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification
        self._needs_output_exporting = needs_output_exporting
        self._needs_review_on_validation_failure = needs_review_on_validation_failure

        self._classification_enabled = classification_enabled
        self._exceptional_queue_enabled = exceptional_queue_enabled

    def make_uploading_step(self) -> Step:
        return Uploading(
            needs_unification=self._needs_unification,
            step_factory=self,
        )

    def make_unification_step(self) -> Step:
        return Unification(
            document_type_id=self._document_type_id,
            container_type=self._container_type,
            needs_image_preprocessing=self._needs_image_preprocessing,
            needs_parsing=self._needs_parsing,
            needs_version_classification=self._needs_version_classification,
            needs_extraction=self._needs_extraction,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            classification_enabled=self._classification_enabled,
            step_factory=self,
        )

    def make_image_preprocessing_step(self) -> Step:
        return ImagePreprocessing(
            document_type_id=self._document_type_id,
            needs_parsing=self._needs_parsing,
            needs_version_classification=self._needs_version_classification,
            needs_extraction=self._needs_extraction,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            classification_enabled=self._classification_enabled,
            step_factory=self,
        )

    def make_parsing_step(self) -> Step:
        return Parsing(
            document_type_id=self._document_type_id,
            needs_version_classification=self._needs_version_classification,
            needs_extraction=self._needs_extraction,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            classification_enabled=self._classification_enabled,
            step_factory=self,
        )

    def make_classification_step(self) -> Step:
        return Classification(document_type_id=self._document_type_id, step_factory=self)

    def make_version_classification_step(self) -> Step:
        return VersionClassification(
            needs_extraction=self._needs_extraction,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            step_factory=self,
        )

    def make_extraction_step(self) -> Step:
        return Extraction(
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            step_factory=self,
        )

    def make_postprocessing_step(self) -> Step:
        return Postprocessing(
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            step_factory=self,
        )

    def make_validation_step(self) -> Step:
        return Validation(
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            needs_review_on_validation_failure=self._needs_review_on_validation_failure,
            step_factory=self,
        )

    def make_manual_review_step(self) -> Step:
        return ManualReview()

    def make_exporting_step(self) -> Step:
        return Exporting(step_factory=self)

    def make_successful_exporting_step(self) -> Step:
        return SuccessfulExporting()

    def make_successful_processing_step(self) -> Step:
        return SuccessfulProcessing()

    def make_failed_processing_step(self) -> Step:
        if self.error.is_system:
            return Failure(step_factory=self)

        if self._exceptional_queue_enabled:
            return ExceptionalQueue(step_factory=self)

        return Postponement(step_factory=self)
