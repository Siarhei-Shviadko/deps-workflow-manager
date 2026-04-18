from pydantic import Field, field_validator

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["SerializedDocumentId"]


class SerializedDocumentId(ConfiguredBaseSerializer):
    document_id: str = Field(..., alias="documentId")

    @field_validator("document_id")
    @classmethod
    def validate_document_id(cls, document_id):
        if not document_id.isdigit():
            raise ValueError(f"Document ID '{document_id}' should be a valid positive integer")

        if int(document_id) < 1:
            raise ValueError(f"Document ID '{document_id}' should be greater than or equal to 1")

        return document_id
