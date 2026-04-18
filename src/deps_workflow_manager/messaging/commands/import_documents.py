from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["ImportDocuments", "ImportDocumentsReply"]


@dataclass
class ImportDocuments(Command):
    paths: list[str]
    source: str


@dataclass
class ImportDocumentsReply(Command):
    documents: list[tuple[str, str]]
