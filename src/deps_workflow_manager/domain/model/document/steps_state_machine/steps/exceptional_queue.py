from ....shared import Error, Status
from .abstract_step import AbstractStep
from .step import Step

__all__ = ["ExceptionalQueue"]


class ExceptionalQueue(AbstractStep):
    def __init__(self, error: Error) -> None:
        self._status = Status.EXCEPTIONAL_QUEUE

        self.error = error

    def __str__(self) -> str:
        return f"<ExceptionalQueue> error: {self.error}"

    def next_step(self) -> Step:
        raise RuntimeError("There is no steps after exceptional queue.")
