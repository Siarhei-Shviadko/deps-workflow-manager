from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from .command_with_error import CommandWithError

__all__ = ["PerformVersionClassification", "PerformVersionClassificationReply"]


@dataclass
class PerformVersionClassification(Command):
    document_id: str
    files: list[str]
    template_id: str


@dataclass
class PerformVersionClassificationReply(CommandWithError):
    document_id: str
    template_id: str
    version_id: str
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
