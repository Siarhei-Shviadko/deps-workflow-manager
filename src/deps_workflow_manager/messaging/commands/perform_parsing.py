from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from .command_with_error import CommandWithError

__all__ = ["PerformParsing", "PerformParsingReply"]


@dataclass
class PerformParsing(Command):
    tenant_id: str
    document_id: str
    files: list[str]
    engine: str
    features: Optional[list[str]] = None
    document_type_id: Optional[str] = None
    language: Optional[str] = None


@dataclass
class PerformParsingReply(CommandWithError):
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
