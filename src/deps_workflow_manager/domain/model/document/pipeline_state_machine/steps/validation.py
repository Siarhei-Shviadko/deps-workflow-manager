from ....shared import Status
from .abstract_step import AbstractStep
from .i_step_factory import IStepFactory
from .step import Step

__all__ = ["Validation"]


class Validation(AbstractStep):
    def __init__(
        self,
        needs_user_verification: bool,
        needs_output_exporting: bool,
        needs_review_on_validation_failure: bool,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.VALIDATION
        self._needs_user_verification = needs_user_verification
        self._needs_output_exporting = needs_output_exporting
        self._needs_review_on_validation_failure = needs_review_on_validation_failure
        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__}> needs_user_verification: {self._needs_user_verification}, "
            f"needs_output_exporting: {self._needs_output_exporting}"
        )

    def next_step(self) -> Step:
        if self._needs_review():
            return self._step_factory.make_manual_review_step()
        if self._needs_output_exporting:
            return self._step_factory.make_exporting_step()

        return self._step_factory.make_successful_processing_step()

    def _needs_review(self) -> bool:
        return self._needs_user_verification or (
            self._needs_review_on_validation_failure and self.is_validation_error_occurred
        )
