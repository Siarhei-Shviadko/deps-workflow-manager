from typing import Optional

from ...shared import Error, Status
from .steps import Step, StepFactory

__all__ = ["PipelineStateMachine"]


class PipelineStateMachine:
    status_step_map = {
        Status.NEW: StepFactory.make_uploading_step,
        Status.UNIFICATION: StepFactory.make_unification_step,
        Status.CLASSIFICATION: StepFactory.make_classification_step,
        Status.VERSION_CLASSIFICATION: StepFactory.make_version_classification_step,
        Status.IMAGE_PREPROCESSING: StepFactory.make_image_preprocessing_step,
        Status.PARSING: StepFactory.make_parsing_step,
        Status.EXTRACTION: StepFactory.make_extraction_step,
        Status.POSTPROCESSING: StepFactory.make_postprocessing_step,
        Status.VALIDATION: StepFactory.make_validation_step,
        Status.NEEDS_REVIEW: StepFactory.make_manual_review_step,
        Status.EXPORTING: StepFactory.make_exporting_step,
        Status.EXPORTED: StepFactory.make_successful_exporting_step,
        Status.EXCEPTIONAL_QUEUE: StepFactory.make_failed_processing_step,
        Status.POSTPONED: StepFactory.make_failed_processing_step,
        Status.FAILURE: StepFactory.make_failed_processing_step,
        Status.COMPLETED: StepFactory.make_successful_processing_step,
    }

    def __init__(
        self,
        current_status: Status,
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
        self._current_status = current_status
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

    @property
    def error(self) -> Optional[Error]:
        return self._error

    @error.setter
    def error(self, error: Optional[Error] = None) -> None:
        self._error = error

    @property
    def document_type_id(self) -> Optional[str]:
        return self._document_type_id

    @document_type_id.setter
    def document_type_id(self, document_type_id: Optional[str] = None) -> None:
        self._document_type_id = document_type_id

    @property
    def container_type(self) -> Optional[str]:
        return self._container_type

    @container_type.setter
    def container_type(self, value: Optional[str] = None) -> None:
        self._container_type = value

    @property
    def step_factory(self) -> StepFactory:
        return StepFactory(
            document_type_id=self._document_type_id,
            container_type=self.container_type,
            error=self._error,
            needs_unification=self._needs_unification,
            needs_image_preprocessing=self._needs_image_preprocessing,
            needs_parsing=self._needs_parsing,
            needs_version_classification=self._needs_version_classification,
            needs_extraction=self._needs_extraction,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            needs_user_verification=self._needs_user_verification,
            needs_output_exporting=self._needs_output_exporting,
            needs_review_on_validation_failure=self._needs_review_on_validation_failure,
            classification_enabled=self._classification_enabled,
            exceptional_queue_enabled=self._exceptional_queue_enabled,
        )

    @property
    def current_step(self) -> Step:
        if (factory_method := self.status_step_map.get(self._current_status)) is None:
            raise RuntimeError("Unsupported document status.")

        return factory_method(self.step_factory)

    @property
    def next_step(self) -> Step:
        return self.current_step.next_step()

    def update(
        self,
        needs_image_preprocessing: bool,
        needs_parsing: bool,
        needs_extraction: bool,
        needs_postprocessing: bool,
        needs_validation: bool,
        needs_user_verification: bool,
        needs_output_exporting: bool,
        needs_review_on_validation_failure: bool,
    ) -> None:
        self._needs_image_preprocessing = needs_image_preprocessing
        self._needs_parsing = needs_parsing
        self._needs_extraction = needs_extraction
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification
        self._needs_output_exporting = needs_output_exporting
        self._needs_review_on_validation_failure = needs_review_on_validation_failure
