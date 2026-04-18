from ....shared import Status
from .abstract_step import AbstractStep
from .i_step_factory import IStepFactory
from .step import Step

__all__ = ["Postprocessing"]


class Postprocessing(AbstractStep):
    def __init__(
        self,
        needs_validation: bool,
        needs_user_verification: bool,
        needs_output_exporting: bool,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.POSTPROCESSING

        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification
        self._needs_output_exporting = needs_output_exporting

        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<{self.__class__.__name__}> needs_validation: {self._needs_validation}, "
            f"needs_user_verification: {self._needs_user_verification}, "
            f"needs_output_exporting: {self._needs_output_exporting}"
        )

    def next_step(self) -> Step:
        if self._needs_validation:
            return self._step_factory.make_validation_step()
        elif self._needs_user_verification:
            return self._step_factory.make_manual_review_step()
        elif self._needs_output_exporting:
            return self._step_factory.make_exporting_step()

        return self._step_factory.make_successful_processing_step()
