from typing import Any, Mapping

from deps_workflow_manager.domain.model import (
    ExtractionType,
    ParsingFeature,
    WorkflowConfiguration,
)

__all__ = ["WorkflowConfigurationMapper"]


class WorkflowConfigurationMapper:
    @staticmethod
    def from_dict(configuration_dict: Mapping[str, Any]) -> WorkflowConfiguration:
        return WorkflowConfiguration(
            tenant_id=configuration_dict["tenant_id"],
            document_type_id=configuration_dict["document_type_id"],
            extraction_type=(
                ExtractionType(configuration_dict["extraction_type"])
                if configuration_dict["extraction_type"]
                else ExtractionType.NON
            ),
            image_transformations=set(configuration_dict["image_transformations"])
            if configuration_dict["image_transformations"]
            else None,
            llm_type=configuration_dict["llm_type"],
            parsing_features={ParsingFeature(feature) for feature in configuration_dict["parsing_features"]}
            if configuration_dict["parsing_features"]
            else None,
            needs_extraction=configuration_dict["needs_extraction"],
            needs_postprocessing=configuration_dict["needs_postprocessing"],
            needs_validation=configuration_dict["needs_validation"],
            needs_user_verification=configuration_dict["needs_user_verification"],
            needs_output_exporting=configuration_dict["needs_output_exporting"],
            needs_review_on_validation_failure=configuration_dict["needs_review_on_validation_failure"],
            engine=configuration_dict["engine"],
        )

    @staticmethod
    def to_dict(configuration: WorkflowConfiguration) -> dict[str, Any]:
        return {
            "tenant_id": configuration.tenant_id,
            "document_type_id": configuration.document_type_id,
            "extraction_type": configuration.extraction_type.value if configuration.extraction_type else None,
            "image_transformations": list(configuration.image_transformations)
            if configuration.image_transformations
            else None,
            "llm_type": configuration.llm_type,
            "parsing_features": list(configuration.parsing_features) if configuration.parsing_features else None,
            "needs_extraction": configuration.needs_extraction,
            "needs_postprocessing": configuration.needs_postprocessing,
            "needs_validation": configuration.needs_validation,
            "needs_user_verification": configuration.needs_user_verification,
            "needs_output_exporting": configuration.needs_output_exporting,
            "needs_review_on_validation_failure": configuration.needs_review_on_validation_failure,
            "engine": configuration.engine,
        }
