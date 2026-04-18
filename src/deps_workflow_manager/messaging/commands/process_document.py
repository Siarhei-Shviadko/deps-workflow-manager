from dataclasses import dataclass

from deps_message_flow.commands.common import Command

from deps_workflow_manager.domain.model import NeedsReviewOption, ParsingFeature

__all__ = ["ProcessDocument"]


@dataclass
class ProcessDocument(Command):
    document_id: str
    tenant_id: str
    files: list[str]
    document_type_id: str | None = None
    engine: str | None = None
    language: str | None = None
    llm_type: str | None = None
    parsing_features: list[ParsingFeature] | None = None
    needs_unification: bool = True
    needs_extraction: bool = True
    needs_parsing: bool | None = None
    needs_validation: bool | None = None
    needs_review: NeedsReviewOption | None = None
    needs_output_exporting: bool | None = None
