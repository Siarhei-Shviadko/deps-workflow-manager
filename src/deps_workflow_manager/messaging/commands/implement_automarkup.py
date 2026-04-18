from dataclasses import dataclass

__all__ = ["ImplementAutoMarkup", "AutoMarkupFailedReply"]

from deps_message_flow.commands.common import Command


@dataclass
class ImplementAutoMarkup(Command):
    template_id: str
    version_id: str
    tenant_id: str


@dataclass
class AutoMarkupFailedReply(Command):
    pass
