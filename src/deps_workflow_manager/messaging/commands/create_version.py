from dataclasses import dataclass
from typing import Optional

__all__ = ["CreateVersion", "CreateVersionReply"]

from deps_message_flow.commands.common import Command


@dataclass
class CreateVersion(Command):
    template_id: str
    tenant_id: str
    name: str
    original_blob_names: list[str]
    preprocessed_blob_names: list[str]
    description: Optional[str]


@dataclass
class CreateVersionReply(Command):
    template_id: str
    name: str
    version_id: Optional[str] = None
