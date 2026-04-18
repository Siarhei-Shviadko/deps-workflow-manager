from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from deps_workflow_manager.domain.model import Status

__all__ = ["StartDocumentProcessing"]


@dataclass
class StartDocumentProcessing(Command):
    document_id: str
    document_name: str
    document_type_id: str
    tenant_id: str
    engine: Optional[str]
    language: Optional[str]
    llm_type: Optional[str]
    assign_to_me: bool
    parsing_features: Optional[list[str]]
    needs_unifier: bool
    needs_extraction: bool
    files: list[str]
    document_metadata: Optional[dict]
    from_step: str = Status.NEW.value
