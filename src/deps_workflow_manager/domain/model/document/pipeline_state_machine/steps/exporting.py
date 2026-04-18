from ....shared import Status
from .abstract_step import AbstractStep
from .i_step_factory import IStepFactory
from .step import Step

__all__ = ["Exporting"]


class Exporting(AbstractStep):
    def __init__(self, *, step_factory: IStepFactory) -> None:
        self._status = Status.EXPORTING
        self._step_factory = step_factory

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}> error: {self.error}"

    def next_step(self) -> Step:
        if self.error:
            return self._step_factory.make_failed_processing_step()

        return self._step_factory.make_successful_exporting_step()
