from typing import Optional

from ..shared import ParsingFeature

__all__ = ["DocumentProcessingInfo"]


class DocumentProcessingInfo:
    def __init__(
        self,
        document_id: str,
        tenant_id: str,
        needs_unifier: bool,
        needs_extraction: bool,
        assign_to_me: bool,
        parsing_features: Optional[set[ParsingFeature]],
    ) -> None:
        self.document_id = document_id
        self.tenant_id = tenant_id
        self.needs_unifier = needs_unifier
        self.needs_extraction = needs_extraction
        self.assign_to_me = assign_to_me
        self.parsing_features = parsing_features

    def __repr__(self):
        return (
            f"DocumentProcessingInfo(document_id={self.document_id!r}, "
            f"tenant_id={self.tenant_id!r}, "
            f"needs_unifier={self.needs_unifier!r}, "
            f"needs_extraction={self.needs_extraction!r}, "
            f"assign_to_me={self.assign_to_me!r}, "
            f"parsing_features={self.parsing_features!r})"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, DocumentProcessingInfo) and all(
            (
                self.document_id == other.document_id,
                self.tenant_id == other.tenant_id,
                self.needs_unifier == other.needs_unifier,
                self.needs_extraction == other.needs_extraction,
                self.assign_to_me == other.assign_to_me,
                self.parsing_features == other.parsing_features,
            ),
        )
