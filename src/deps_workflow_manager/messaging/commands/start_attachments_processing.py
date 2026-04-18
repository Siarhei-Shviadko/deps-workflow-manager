from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from deps_workflow_manager.domain.model import Status

__all__ = ["StartAttachmentsProcessing"]


@dataclass
class StartAttachmentsProcessing(Command):
    documents: list[tuple[str, str]]
    tenant_id: str
    parent_id: str
    engine: Optional[str]
    language: Optional[str]
    assign_to_me: bool
    parsing_features: Optional[list[str]]
    needs_unifier: bool
    needs_extraction: bool
    document_type_id: Optional[str] = None
    document_metadata: Optional[dict] = None
    from_step: str = Status.NEW.value
    llm_type: Optional[str] = None
