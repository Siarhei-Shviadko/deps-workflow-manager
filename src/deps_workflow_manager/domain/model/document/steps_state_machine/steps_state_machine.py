from typing import Optional

from deps_workflow_manager.domain.model.document.steps_state_machine import (
    Step,
    StepFactory,
)

from ...shared import Error, Status

__all__ = ["StepStateMachine"]


class StepStateMachine:
    status_step_map = {
        Status.NEW: StepFactory.make_uploading_step,
        Status.UNIFICATION: StepFactory.make_unification_step,
        Status.CLASSIFICATION: StepFactory.make_classification_step,
        Status.IMAGE_PREPROCESSING: StepFactory.make_image_preprocessing_step,
        Status.PARSING: StepFactory.make_parsing_step,
        Status.EXTRACTION: StepFactory.make_extraction_step,
        Status.POSTPROCESSING: StepFactory.make_postprocessing_step,
        Status.VALIDATION: StepFactory.make_validation_step,
        Status.NEEDS_REVIEW: StepFactory.make_manual_review_step,
        Status.EXCEPTIONAL_QUEUE: StepFactory.make_business_failed_step,
        Status.POSTPONED: StepFactory.make_business_failed_step,
        Status.FAILURE: StepFactory.make_system_failed_step,
        Status.COMPLETED: StepFactory.make_successful_processing_step,
    }

    def __init__(
        self,
        current_status: Status,
        document_type: Optional[str] = None,
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
        self._current_status = current_status
        self._document_type = document_type
        self._needs_unification = needs_unification
        self._classification_enabled = classification_enabled
        self._needs_image_preprocessing = needs_image_preprocessing
        self._needs_parsing = needs_parsing
        self._needs_extraction = needs_extraction
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation
        self.error = error
        self._needs_exceptional_queue = needs_exceptional_queue
        self._needs_user_verification = needs_user_verification

    @property
    def step_factory(self) -> StepFactory:
        return StepFactory(
            document_type=self._document_type,
            needs_unification=self._needs_unification,
            classification_enabled=self._classification_enabled,
            needs_image_preprocessing=self._needs_image_preprocessing,
            needs_parsing=self._needs_parsing,
            needs_extraction=self._needs_extraction,
            needs_postprocessing=self._needs_postprocessing,
            needs_validation=self._needs_validation,
            error=self.error,
            needs_exceptional_queue=self._needs_exceptional_queue,
            needs_user_verification=self._needs_user_verification,
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
        needs_postprocessing: bool,
        needs_validation: bool,
        needs_user_verification: bool,
    ) -> None:
        self._needs_image_preprocessing = needs_image_preprocessing
        self._needs_parsing = needs_parsing
        self._needs_postprocessing = needs_postprocessing
        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification
