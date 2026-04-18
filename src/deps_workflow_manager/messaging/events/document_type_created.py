from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentTypeCreated"]


@dataclass
class DocumentTypeCreated(DomainEvent):
    document_type: str
    tenant: str
