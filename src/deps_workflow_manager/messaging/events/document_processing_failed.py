from dataclasses import dataclass

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentProcessingFailed"]


@dataclass
class DocumentProcessingFailed(DomainEvent):
    document_id: str
    message: str
