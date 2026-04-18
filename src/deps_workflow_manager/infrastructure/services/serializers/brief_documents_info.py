from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from deps_workflow_manager.domain.model import Document, DocumentState

__all__ = ["GetBriefDocumentsInfoResponse", "BriefDocumentInfo"]


class BriefDocumentInfo(BaseModel):
    id: str
    title: str
    state: DocumentState
    files: list[str]
    type_id: Optional[str] = Field(None, alias="typeId")
    engine: Optional[str] = None
    language: Optional[str] = None
    llm_type: Optional[str] = None
    error_in_state: Optional[DocumentState] = Field(None, alias="errorInState")
    metadata: Optional[dict[str, Any]]
    parent_id: Optional[str] = Field(None, alias="parentId")

    model_config = SettingsConfigDict(populate_by_name=True)

    def to_model(self) -> Document:
        return Document(
            id_=self.id,
            title=self.title,
            state=self.state,
            files=self.files,
            type_id=self.type_id,
            engine=self.engine,
            language=self.language,
            llm_type=self.llm_type,
            error_in_state=self.error_in_state,
            metadata=self.metadata,
            parent_id=self.parent_id,
        )


class GetBriefDocumentsInfoResponse(BaseModel):
    documents: list[BriefDocumentInfo]
