from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["PreprocessReferencePage", "PreprocessReferencePageReply"]


@dataclass
class PreprocessReferencePage(Command):
    template_id: str
    blob_names: list[str]


@dataclass
class PreprocessReferencePageReply(Command):
    template_id: str
    blob_names: list[str]
