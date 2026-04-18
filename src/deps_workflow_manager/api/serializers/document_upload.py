from typing import Optional

from pydantic import Field

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["UploadDocumentResponse"]


class UploadDocumentResponse(ConfiguredBaseSerializer):
    document_id: str = Field(..., alias="id")
    message: Optional[str] = None
