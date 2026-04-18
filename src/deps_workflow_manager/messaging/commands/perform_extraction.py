from dataclasses import dataclass, field
from typing import Optional, TypedDict

from deps_message_flow.commands.common import Command

from .command_with_error import CommandWithError

__all__ = ["PerformExtraction", "PerformExtractionReply"]


class ExtraData(TypedDict, total=False):
    template_version_id: Optional[str]


@dataclass
class PerformExtraction(Command):
    tenant_id: str
    document_id: str
    document_type_id: str
    language: Optional[str] = None
    engine: Optional[str] = None
    llm_type: Optional[str] = None
    extra_data: ExtraData = field(default_factory=dict)  # type: ignore


@dataclass
class PerformExtractionReply(CommandWithError):
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
