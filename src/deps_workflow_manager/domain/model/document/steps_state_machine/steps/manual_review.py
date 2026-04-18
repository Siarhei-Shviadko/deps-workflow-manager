from ....shared import Status
from .abstract_step import AbstractStep
from .step import Step

__all__ = ["ManualReview"]


class ManualReview(AbstractStep):
    def __init__(self) -> None:
        self._status = Status.NEEDS_REVIEW

    def __str__(self) -> str:
        return "<ManualReview>"

    def next_step(self) -> Step:
        raise RuntimeError("There is no steps after manual review.")
