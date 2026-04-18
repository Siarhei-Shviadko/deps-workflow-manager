from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from .command_with_error import CommandWithError

__all__ = ["PerformExporting", "PerformExportingReply"]


@dataclass
class PerformExporting(Command):
    document_id: str
    document_type_id: str
    profile_ids: Optional[list[str]]


@dataclass
class PerformExportingReply(CommandWithError):
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
