import abc
from typing import Optional

from ....shared import Error, Status
from .istep_factory import IStepFactory
from .step import Step

__all__ = ["AbstractStep"]


class AbstractStep(abc.ABC):
    _status: Status
    _error: Optional[Error]
    _step_factory: IStepFactory

    @property
    def status(self) -> Status:
        return self._status

    @property
    def error(self) -> Optional[Error]:  # type: ignore
        if hasattr(self, "_error"):
            return self._error

    @error.setter
    def error(self, error: Optional[Error]) -> None:
        self._error = error

        if hasattr(self, "_step_factory"):
            self._step_factory.error = error

    @property
    def is_error_occurred(self) -> bool:
        return self.error is not None

    @property
    def is_business_error_occurred(self) -> bool:
        return self.is_error_occurred and self.error.is_business

    @property
    def is_system_error_occurred(self) -> bool:
        return self.is_error_occurred and self.error.is_system

    @abc.abstractmethod
    def next_step(self) -> Step:
        pass
