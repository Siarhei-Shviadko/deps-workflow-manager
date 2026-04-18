from typing import Protocol

__all__ = ["Step"]


class Step(Protocol):
    def next_step(self) -> "Step":
        pass
