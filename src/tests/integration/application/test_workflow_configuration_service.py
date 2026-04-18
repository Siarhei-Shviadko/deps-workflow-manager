import uuid

from deps_workflow_manager.application import WorkflowConfigurationService
from deps_workflow_manager.domain.model import (
    DocumentTypeInfo,
    ExtractionType,
    NeedsReviewOption,
    ParsingFeature,
    WorkflowConfiguration,
)
from deps_workflow_manager.infrastructure.repositories import (
    WorkflowConfigurationRepository,
)


def test_workflow_configuration_service__save_configuration__configuration_created(
    workflow_configuration_service,
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_service.save_configuration(workflow_configuration)

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration.tenant_id,
            document_type_id=workflow_configuration.document_type_id,
        )
        == workflow_configuration
    )


def test_workflow_configuration_service__save_configuration__configuration_updated(
    workflow_configuration_service,
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_service.save_configuration(workflow_configuration)

    workflow_configuration.image_transformations = {"a", "b", "c"}

    workflow_configuration_service.save_configuration(workflow_configuration)

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration.tenant_id,
            document_type_id=workflow_configuration.document_type_id,
        )
        == workflow_configuration
    )


def test_workflow_configuration_service__save_configuration_for__configuration_created(
    workflow_configuration_service,
    workflow_configuration_repo,
):
    document_type_info = DocumentTypeInfo(
        tenant_id="abc",
        document_type_id="xyz",
        image_transformations={"jdfg", "jfndkj"},
        extraction_type=ExtractionType.PLUGIN,
        llm_type="gpt-4",
    )

    workflow_configuration_service.save_configuration_for(document_types=[document_type_info])
    assert workflow_configuration_repo.find(
        tenant_id=document_type_info.tenant_id,
        document_type_id=document_type_info.document_type_id,
    ) == WorkflowConfiguration(
        tenant_id=document_type_info.tenant_id,
        document_type_id=document_type_info.document_type_id,
        image_transformations=document_type_info.image_transformations,
        extraction_type=document_type_info.extraction_type,
        llm_type=document_type_info.llm_type,
        needs_extraction=True,
        needs_output_exporting=False,
        needs_review_on_validation_failure=False,
        needs_user_verification=True,
        needs_validation=False,
        needs_postprocessing=False,
        parsing_features={ParsingFeature.TEXT},
    )


def test_workflow_configuration_service__save_configuration_for__configuration_updated(
    workflow_configuration_service,
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_repo.save(workflow_configuration)

    document_type_info = DocumentTypeInfo(
        tenant_id=workflow_configuration.tenant_id,
        document_type_id=workflow_configuration.document_type_id,
        image_transformations={"jdfg", "jfndkj"},
        extraction_type=ExtractionType.PLUGIN,
        llm_type="gpt-4",
    )
    workflow_configuration_service.save_configuration_for(document_types=[document_type_info])

    assert workflow_configuration_repo.find(
        tenant_id=document_type_info.tenant_id,
        document_type_id=document_type_info.document_type_id,
    ) == WorkflowConfiguration(
        tenant_id=document_type_info.tenant_id,
        document_type_id=document_type_info.document_type_id,
        image_transformations=document_type_info.image_transformations,
        extraction_type=document_type_info.extraction_type,
        llm_type=document_type_info.llm_type,
        needs_validation=workflow_configuration.needs_validation,
        needs_postprocessing=workflow_configuration.needs_postprocessing,
        needs_user_verification=workflow_configuration.needs_user_verification,
        needs_output_exporting=workflow_configuration.needs_output_exporting,
        needs_review_on_validation_failure=workflow_configuration.needs_review_on_validation_failure,
    )


def test_workflow_configuration_service__update_configuration__configuration_updated(
    workflow_configuration_service: WorkflowConfigurationService,
    workflow_configuration_repo: WorkflowConfigurationRepository,
    workflow_configuration: WorkflowConfiguration,
):
    workflow_configuration_repo.save(workflow_configuration)
    new_llm_type = uuid.uuid4().hex
    new_parsing_features = {ParsingFeature.TABLES, ParsingFeature.IMAGES}
    new_needs_validation = not workflow_configuration.needs_validation
    new_needs_output_exporting = not workflow_configuration.needs_output_exporting
    needs_review = next((el for el in list(NeedsReviewOption) if el != workflow_configuration.needs_review))

    workflow_configuration_service.update_configuration(
        document_type_id=workflow_configuration.document_type_id,
        tenant_id=workflow_configuration.tenant_id,
        llm_type=new_llm_type,
        parsing_features=new_parsing_features,
        needs_validation=new_needs_validation,
        needs_output_exporting=new_needs_output_exporting,
        needs_review=needs_review,
    )

    assert workflow_configuration_repo.find(
        tenant_id=workflow_configuration.tenant_id,
        document_type_id=workflow_configuration.document_type_id,
    ) == WorkflowConfiguration(
        tenant_id=workflow_configuration.tenant_id,
        document_type_id=workflow_configuration.document_type_id,
        image_transformations=workflow_configuration.image_transformations,
        extraction_type=workflow_configuration.extraction_type,
        llm_type=new_llm_type,
        parsing_features=new_parsing_features,
        needs_validation=new_needs_validation,
        needs_postprocessing=workflow_configuration.needs_postprocessing,
        needs_user_verification=needs_review == NeedsReviewOption.ALWAYS_REVIEW,
        needs_output_exporting=new_needs_output_exporting,
        needs_review_on_validation_failure=needs_review == NeedsReviewOption.REVIEW_IF_VALIDATION_FAILURE,
        engine=workflow_configuration.engine,
    )


def test_workflow_configuration_service__delete_configuration__configuration_deleted(
    workflow_configuration_service,
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_repo.save(workflow_configuration)
    workflow_configuration_service.delete_configuration(
        tenant_id=workflow_configuration.tenant_id,
        document_type_id=workflow_configuration.document_type_id,
    )

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration.tenant_id,
            document_type_id=workflow_configuration.document_type_id,
        )
        is None
    )


def test_workflow_configuration_service__find_configuration__configuration_exists(
    workflow_configuration_service,
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_repo.save(workflow_configuration)

    assert (
        workflow_configuration_service.find_configuration(
            tenant_id=workflow_configuration.tenant_id,
            document_type_id=workflow_configuration.document_type_id,
        )
        == workflow_configuration
    )


def test_workflow_configuration_service__find_configuration__configuration_does_not_exist(
    workflow_configuration_service,
    workflow_configuration,
):
    assert (
        workflow_configuration_service.find_configuration(
            tenant_id=workflow_configuration.tenant_id,
            document_type_id=workflow_configuration.document_type_id,
        )
        is None
    )
