from dataclasses import dataclass
from typing import Optional

from deps_message_flow.events.common import DomainEvent

__all__ = ["ExtractorAttached"]


@dataclass
class ExtractorAttached(DomainEvent):
    document_type_id: str
    extraction_type: str
    language: Optional[str] = None
    engine: Optional[str] = None
    description: Optional[str] = None
    image_transformations: Optional[list[str]] = None
