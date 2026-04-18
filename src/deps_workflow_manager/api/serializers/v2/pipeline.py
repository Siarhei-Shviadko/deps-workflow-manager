from typing import Optional

from pydantic import Field, field_validator

from deps_workflow_manager.domain.model import ParsingFeature, Status

from ..configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["RunPipelineFromStepRequest"]


class RunPipelineFromStepRequest(ConfiguredBaseSerializer):
    document_ids: list[str] = Field(..., alias="documentIds", min_items=1)
    step: Status
    engine: Optional[str] = Field(None, alias="engineName")
    language: Optional[str] = Field(None)
    llm_type: Optional[str] = Field(None, alias="llmType")
    parsing_features: Optional[set[ParsingFeature]] = Field(None, alias="parsingFeatures")

    @field_validator("document_ids")
    @classmethod
    def validate_document_id(cls, document_ids):
        for document_id in document_ids:
            if not document_id.isdigit():
                raise ValueError(f"Document ID '{document_id}' should be a valid positive integer")

            if int(document_id) < 1:
                raise ValueError(f"Document ID '{document_id}' should be greater than or equal to 1")

        return document_ids
