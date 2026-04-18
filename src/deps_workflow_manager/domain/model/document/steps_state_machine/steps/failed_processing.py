from ....shared import Error, Status
from .abstract_step import AbstractStep
from .step import Step

__all__ = ["FailedProcessing"]


class FailedProcessing(AbstractStep):
    def __init__(self, error: Error) -> None:
        self._status = Status.FAILURE

        self.error = error

    def __str__(self) -> str:
        return f"<FailedProcessing> error: {self.error}"

    def next_step(self) -> Step:
        raise RuntimeError("There is no next step after failed processing.")
