from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from deps_workflow_manager.domain.model import Error

__all__ = ["UpdateDocumentState"]


@dataclass
class UpdateDocumentState(Command):
    document_id: str
    state: str
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    def __init__(self, document_id: str, state: str, error: Optional[Error] = None) -> None:
        self.document_id = document_id
        self.state = state
        self.error_type = None if error is None else error.type.value
        self.error_message = None if error is None else error.message
