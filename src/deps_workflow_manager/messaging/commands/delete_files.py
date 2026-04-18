from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["DeleteFiles"]


@dataclass
class DeleteFiles(Command):
    file_paths: list[str]
