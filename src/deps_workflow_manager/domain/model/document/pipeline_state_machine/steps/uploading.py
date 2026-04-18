from ....shared import Status
from .abstract_step import AbstractStep
from .i_step_factory import IStepFactory
from .step import Step

__all__ = ["Uploading"]


class Uploading(AbstractStep):
    def __init__(self, needs_unification: bool, *, step_factory: IStepFactory) -> None:
        self._status = Status.NEW

        self._needs_unification = needs_unification
        self._step_factory = step_factory

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}> needs_unification: {self._needs_unification}"

    def next_step(self) -> Step:
        if self.is_error_occurred:
            return self._step_factory.make_failed_processing_step()
        elif self._needs_unification:
            return self._step_factory.make_unification_step()

        return self._step_factory.make_successful_processing_step()
