from ....shared import Status
from .abstract_step import AbstractStep
from .step import Step

__all__ = ["SuccessfulProcessing"]


class SuccessfulProcessing(AbstractStep):
    def __init__(self) -> None:
        self._status = Status.COMPLETED

    def __str__(self) -> str:
        return "<SuccessfulProcessing>"

    def next_step(self) -> Step:
        raise RuntimeError("There is no steps after successful processing.")
