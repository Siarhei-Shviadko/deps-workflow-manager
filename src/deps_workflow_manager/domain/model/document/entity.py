from typing import Any, Optional

from ..guards import Guard, ImmutableCheck
from .state import DocumentState

__all__ = ["Document"]


class Document:  # noqa: WPS230
    id = Guard[str](str, ImmutableCheck())
    title = Guard[str](str, ImmutableCheck())
    state = Guard[DocumentState](DocumentState, ImmutableCheck())
    files = Guard[list](list, ImmutableCheck())
    type_id = Guard[str](str, ImmutableCheck())
    engine = Guard[str](str, ImmutableCheck())
    language = Guard[str](str, ImmutableCheck())
    llm_type = Guard[str](str, ImmutableCheck())
    error_in_state = Guard[DocumentState](DocumentState, ImmutableCheck())
    metadata = Guard[dict](dict, ImmutableCheck())
    parent_id = Guard[str](str, ImmutableCheck())

    def __init__(
        self,
        id_: str,
        title: str,
        state: DocumentState,
        files: list[str],
        type_id: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        error_in_state: Optional[DocumentState] = None,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ):
        self.id = id_
        self.title = title
        self.state = state
        self.files = files

        if type_id:
            self.type_id = type_id

        if engine:
            self.engine = engine

        if language:
            self.language = language

        if llm_type:
            self.llm_type = llm_type

        if error_in_state:
            self.error_in_state = error_in_state

        if metadata:
            self.metadata = metadata

        if parent_id:
            self.parent_id = parent_id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Document) and self.id == other.id
