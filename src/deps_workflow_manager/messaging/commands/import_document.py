from dataclasses import dataclass
from typing import Any, Optional

from deps_message_flow.commands.common import Command

__all__ = ["ImportDocument"]


@dataclass
class ImportDocument(Command):
    document_name: str
    document_metadata: dict[str, Any]
    file_path: str
    document_type: str
    invoke_unifier: bool = True
    invoke_extraction: bool = True
    parsing_features: Optional[list[str]] = None
    language: Optional[str] = None
    engine: Optional[str] = None
    llm_type: Optional[str] = None
