from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

__all__ = ["PerformTemplateExtraction", "PerformTemplateExtractionReply"]


@dataclass
class PerformTemplateExtraction(Command):
    template_id: str
    tenant_id: str
    document_id: int
    version_id: Optional[str] = None
    language: Optional[str] = None
    engine: Optional[str] = None


@dataclass
class PerformTemplateExtractionReply(Command):
    document_id: int
