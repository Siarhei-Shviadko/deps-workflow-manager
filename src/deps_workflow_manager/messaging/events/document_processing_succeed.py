from dataclasses import dataclass
from typing import Optional

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentProcessingSucceed"]


@dataclass
class DocumentProcessingSucceed(DomainEvent):
    document_id: str
    document_type: Optional[str] = None
