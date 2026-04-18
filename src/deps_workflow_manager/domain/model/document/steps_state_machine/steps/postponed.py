from ....shared import Error, Status
from .abstract_step import AbstractStep
from .step import Step

__all__ = ["Postponed"]


class Postponed(AbstractStep):
    def __init__(self, error: Error) -> None:
        self._status = Status.POSTPONED

        self.error = error

    def __str__(self) -> str:
        return f"<Postponed> error: {self.error}"

    def next_step(self) -> Step:
        raise RuntimeError("There is no steps after postponing document.")
