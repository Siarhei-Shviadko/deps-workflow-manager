from dataclasses import dataclass

from deps_message_flow.commands.common import Command

from deps_workflow_manager.domain.model import ParsingFeature

__all__ = ["ProcessDocuments"]


@dataclass
class ProcessDocuments(Command):
    documents: list[tuple[str, str]]
    tenant_id: str
    document_type_id: str | None = None
    engine: str | None = None
    language: str | None = None
    llm_type: str | None = None
    assign_to_me: bool = False
    invoke_unifier: bool = False
    invoke_extraction: bool = False
    parsing_features: list[ParsingFeature] | None = None
