from dataclasses import dataclass
from typing import Any, Dict

from deps_message_flow.events.common import DomainEvent

__all__ = ["DocumentReviewCompleted"]


@dataclass
class DocumentReviewCompleted(DomainEvent):
    document_id: str
    document_metadata: Dict[str, Any]
