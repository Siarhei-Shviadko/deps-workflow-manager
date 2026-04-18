from pydantic import Field

from deps_workflow_manager.domain.model import (
    NeedsReviewOption,
    ParsingFeature,
    WorkflowConfiguration,
)

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = ["WorkflowConfigurationResponse"]


class WorkflowConfigurationResponse(ConfiguredBaseSerializer):
    parsing_features: set[ParsingFeature] | None = Field(..., alias="parsingFeatures")
    needs_extraction: bool = Field(..., alias="needsExtraction")
    needs_postprocessing: bool = Field(..., alias="needsPostprocessing")
    needs_validation: bool = Field(..., alias="needsValidation")
    needs_review: NeedsReviewOption = Field(..., alias="needsReview")
    needs_output_exporting: bool = Field(..., alias="needsOutputExporting")

    @classmethod
    def from_domain(cls, configuration: WorkflowConfiguration) -> "WorkflowConfigurationResponse":
        return cls(
            parsing_features=configuration.parsing_features,
            needs_extraction=configuration.needs_extraction,
            needs_postprocessing=configuration.needs_postprocessing,
            needs_validation=configuration.needs_validation,
            needs_review=configuration.needs_review,
            needs_output_exporting=configuration.needs_output_exporting,
        )
