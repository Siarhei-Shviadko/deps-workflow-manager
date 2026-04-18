from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentTypeUpdated"]


@dataclass
class DocumentTypeUpdated(DomainEvent):
    document_type: str
    tenant: str
    llm_type: str | None = None
    engine: str | None = None
