from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

__all__ = ["PerformPreprocess", "PerformPreprocessReply"]


@dataclass
class PerformPreprocess(Command):
    document_id: str
    image_transformations: Optional[list[str]] = None


@dataclass
class PerformPreprocessReply(Command):
    document_id: str
