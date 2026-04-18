from ....shared import Status
from .abstract_step import AbstractStep
from .step import Step

__all__ = ["SuccessfulExporting"]


class SuccessfulExporting(AbstractStep):
    def __init__(self) -> None:
        self._status = Status.EXPORTED

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"

    def next_step(self) -> Step:
        raise RuntimeError("There is no steps after successful exporting.")
