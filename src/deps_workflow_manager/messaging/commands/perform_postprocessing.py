from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["PerformPostprocessing", "PerformPostprocessingReply"]


@dataclass
class PerformPostprocessing(Command):
    document_id: str


@dataclass
class PerformPostprocessingReply(Command):
    document_id: str
