from ....shared import Status
from .abstract_step import AbstractStep
from .istep_factory import IStepFactory
from .step import Step

__all__ = ["Postprocessing"]


class Postprocessing(AbstractStep):
    def __init__(
        self,
        needs_validation: bool,
        needs_user_verification: bool,
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.POSTPROCESSING

        self._needs_validation = needs_validation
        self._needs_user_verification = needs_user_verification

        self._step_factory = step_factory

    def __str__(self) -> str:
        return (
            f"<Postprocessing> needs_validation: {self._needs_validation}, "
            f"needs_user_verification: {self._needs_user_verification}"
        )

    @property
    def is_validation_needed(self) -> bool:
        return self._needs_validation

    @property
    def is_user_verification_needed(self) -> bool:
        return self._needs_user_verification

    def next_step(self) -> Step:
        if self.is_validation_needed:
            return self._step_factory.make_validation_step()
        elif self.is_user_verification_needed:
            return self._step_factory.make_manual_review_step()

        return self._step_factory.make_successful_processing_step()
