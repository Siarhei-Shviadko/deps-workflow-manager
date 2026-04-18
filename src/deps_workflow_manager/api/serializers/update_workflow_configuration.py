from typing import Optional

from pydantic import Field

from deps_workflow_manager.domain.model import NeedsReviewOption, ParsingFeature

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["UpdateWorkflowConfigurationRequest"]


class UpdateWorkflowConfigurationRequest(ConfiguredBaseSerializer):
    document_type_id: str = Field(..., alias="documentTypeId")
    parsing_features: Optional[set[ParsingFeature]] = Field(default=None, alias="parsingFeatures")
    needs_extraction: Optional[bool] = Field(default=None, alias="needsExtraction")
    needs_postprocessing: Optional[bool] = Field(default=None, alias="needsPostprocessing")
    needs_validation: Optional[bool] = Field(default=None, alias="needsValidation")
    needs_review: Optional[NeedsReviewOption] = Field(default=None, alias="needsReview")
    needs_output_exporting: Optional[bool] = Field(default=None, alias="needsOutputExporting")
