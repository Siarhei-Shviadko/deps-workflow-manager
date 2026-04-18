from dataclasses import dataclass
from typing import Any

from deps_message_flow.commands.common import Command

__all__ = ["GetDocumentTypes", "GetDocumentTypesReply"]


@dataclass
class GetDocumentTypes(Command):
    pass


@dataclass
class GetDocumentTypesReply(Command):
    document_types: list[dict[str, Any]]
