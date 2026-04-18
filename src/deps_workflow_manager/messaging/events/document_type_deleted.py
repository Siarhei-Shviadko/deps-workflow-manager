from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentTypeDeleted"]


@dataclass
class DocumentTypeDeleted(DomainEvent):
    document_type: str
    tenant: str
