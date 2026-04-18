from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from .command_with_error import CommandWithError

__all__ = ["PerformClassification", "PerformClassificationReply"]


@dataclass
class PerformClassification(Command):
    document_id: str


@dataclass
class PerformClassificationReply(CommandWithError):
    document_type_id: Optional[str]
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
