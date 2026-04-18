from typing import Optional

from pydantic import Field

from deps_workflow_manager.domain.constants import TemplatePipelineStep

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["RunTemplatePipelineRequest", "RunTemplatePipelineFromStepRequest"]


class RunTemplatePipelineRequest(ConfiguredBaseSerializer):
    document_ids: list[str] = Field(..., alias="documentIds")
    engine: Optional[str] = Field(None, alias="engineName")
    language: Optional[str] = Field(None)
    invoke_unifier: bool = Field(True, alias="unifyData")
    invoke_preprocessor: bool = Field(True, alias="preprocessData")
    invoke_extraction: bool = Field(True, alias="extractData")


class RunTemplatePipelineFromStepRequest(ConfiguredBaseSerializer):
    document_ids: list[str] = Field(..., alias="documentIds")
    step: TemplatePipelineStep
    engine: Optional[str] = Field(None, alias="engineName")
    language: Optional[str] = Field(None)
