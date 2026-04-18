from ....shared import Status
from .abstract_step import AbstractStep
from .istep_factory import IStepFactory
from .step import Step

__all__ = ["Uploading"]


class Uploading(AbstractStep):
    def __init__(self, needs_unification: bool, *, step_factory: IStepFactory) -> None:
        self._status = Status.NEW

        self._needs_unification = needs_unification
        self._step_factory = step_factory

    def __str__(self) -> str:
        return f"<Uploading> needs_unification: {self._needs_unification}"

    @property
    def is_unification_needed(self) -> bool:
        return self._needs_unification

    def next_step(self) -> Step:
        if self.is_unification_needed:
            return self._step_factory.make_unification_step()

        return self._step_factory.make_successful_processing_step()
