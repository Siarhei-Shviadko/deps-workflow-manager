from typing import Optional

from ....shared import Error, ErrorType, Status
from .abstract_step import AbstractStep
from .i_step_factory import IStepFactory
from .step import Step

__all__ = ["Classification"]


class Classification(AbstractStep):
    def __init__(
        self,
        document_type_id: Optional[str],
        *,
        step_factory: IStepFactory,
    ) -> None:
        self._status = Status.CLASSIFICATION

        self._document_type_id = document_type_id

        self._step_factory = step_factory

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}> document_type_id: {self._document_type_id}, " f"error: {self.error}"

    @property
    def is_classification_failed(self) -> bool:
        return self.is_error_occurred or self._document_type_id is None

    def next_step(self) -> Step:
        if self.is_classification_failed:
            self.error = self.error or Error(type_=ErrorType.SYSTEM, message="Classification failed")
            return self._step_factory.make_failed_processing_step()

        return self._step_factory.make_unification_step()
