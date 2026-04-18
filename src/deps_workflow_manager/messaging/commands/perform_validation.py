from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["PerformValidation", "PerformValidationReply"]


@dataclass
class PerformValidation(Command):
    document_id: str
    document_type_id: str


@dataclass
class PerformValidationReply(Command):
    result: bool
