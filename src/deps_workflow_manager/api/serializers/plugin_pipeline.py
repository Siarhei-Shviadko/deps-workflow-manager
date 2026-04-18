from typing import Optional

from pydantic import Field

from deps_workflow_manager.domain.constants import PluginPipelineStep

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["RunPluginPipelineRequest", "RunPluginPipelineFromStepRequest"]


class RunPluginPipelineRequest(ConfiguredBaseSerializer):
    document_ids: list[str] = Field(..., alias="documentIds")
    engine: Optional[str] = Field(None, alias="engineName")
    language: Optional[str] = Field(None)
    llm_type: Optional[str] = Field(None, alias="llmType")
    invoke_unifier: bool = Field(True, alias="unifyData")
    invoke_extraction: bool = Field(True, alias="extractData")


class RunPluginPipelineFromStepRequest(ConfiguredBaseSerializer):
    document_ids: list[str] = Field(..., alias="documentIds")
    step: PluginPipelineStep
    engine: Optional[str] = Field(None, alias="engineName")
    language: Optional[str] = Field(None)
    llm_type: Optional[str] = Field(None, alias="llmType")
