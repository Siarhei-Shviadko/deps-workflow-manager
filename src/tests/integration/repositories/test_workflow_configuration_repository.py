from deps_workflow_manager.domain.model import (
    DocumentTypeInfo,
    ExtractionType,
    WorkflowConfiguration,
)


def test_workflow_configuration_repository__find__config_does_not_exist(workflow_configuration_repo):
    assert workflow_configuration_repo.find("test", "test") is None


def test_workflow_configuration_repository__find__config_exists(workflow_configuration_repo, workflow_configuration):
    workflow_configuration_repo.save(workflow_configuration)
    workflow_configuration_repo.save(
        WorkflowConfiguration(tenant_id=workflow_configuration.tenant_id, document_type_id="x")
    )
    workflow_configuration_repo.save(
        WorkflowConfiguration(tenant_id="x", document_type_id=workflow_configuration.document_type_id)
    )

    assert (
        workflow_configuration_repo.find(workflow_configuration.tenant_id, workflow_configuration.document_type_id)
        == workflow_configuration
    )


def test_workflow_configuration_repository__save__configuration_updated(
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_repo.save(workflow_configuration)

    workflow_configuration.image_transformations = {"grayscaling", "blurring"}
    workflow_configuration.extraction_type = ExtractionType.PLUGIN
    workflow_configuration.needs_validation = True

    workflow_configuration_repo.save(workflow_configuration)

    assert (
        workflow_configuration_repo.find(workflow_configuration.tenant_id, workflow_configuration.document_type_id)
        == workflow_configuration
    )


def test_workflow_configuration_repository__save_for__configuration_created(
    workflow_configuration_repo,
):
    document_type_info = DocumentTypeInfo(
        tenant_id="abc",
        document_type_id="xyz",
        image_transformations={"jdfg", "jfndkj"},
        extraction_type=ExtractionType.PLUGIN,
        llm_type="gpt-4",
        engine="tesseract",
    )
    workflow_configuration_repo.save_for(document_types=[document_type_info])

    created_workflow_configuration = workflow_configuration_repo.find(
        document_type_info.tenant_id, document_type_info.document_type_id
    )

    assert created_workflow_configuration.extraction_type == document_type_info.extraction_type
    assert created_workflow_configuration.image_transformations == document_type_info.image_transformations
    assert created_workflow_configuration.needs_extraction
    assert not created_workflow_configuration.needs_validation
    assert not created_workflow_configuration.needs_postprocessing
    assert not created_workflow_configuration.needs_user_verification
    assert not created_workflow_configuration.needs_output_exporting
    assert created_workflow_configuration.llm_type == document_type_info.llm_type
    assert created_workflow_configuration.engine == document_type_info.engine


def test_workflow_configuration_repository__save_for__configuration_updated(
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_repo.save(workflow_configuration)

    document_type_info = DocumentTypeInfo(
        tenant_id=workflow_configuration.tenant_id,
        document_type_id=workflow_configuration.document_type_id,
        image_transformations={"lsdfbknl", "kflb"},
        extraction_type=ExtractionType.PLUGIN,
        llm_type="gpt-4",
        engine="not tesseract",
    )

    workflow_configuration_repo.save_for(document_types=[document_type_info])

    updated_workflow_configuration = workflow_configuration_repo.find(
        workflow_configuration.tenant_id, workflow_configuration.document_type_id
    )

    assert updated_workflow_configuration.extraction_type == document_type_info.extraction_type
    assert updated_workflow_configuration.image_transformations == document_type_info.image_transformations
    assert updated_workflow_configuration.needs_validation == workflow_configuration.needs_validation
    assert updated_workflow_configuration.needs_postprocessing == workflow_configuration.needs_postprocessing
    assert updated_workflow_configuration.needs_user_verification == workflow_configuration.needs_user_verification
    assert updated_workflow_configuration.needs_output_exporting == workflow_configuration.needs_output_exporting
    assert (
        updated_workflow_configuration.needs_review_on_validation_failure
        == workflow_configuration.needs_review_on_validation_failure
    )
    assert updated_workflow_configuration.llm_type == document_type_info.llm_type
    assert updated_workflow_configuration.engine == document_type_info.engine


def test_workflow_configuration_repository__delete__configuration_deleted(
    workflow_configuration_repo,
    workflow_configuration,
):
    workflow_configuration_1 = WorkflowConfiguration(tenant_id=workflow_configuration.tenant_id, document_type_id="x")
    workflow_configuration_2 = WorkflowConfiguration(
        tenant_id="x", document_type_id=workflow_configuration.document_type_id
    )

    workflow_configuration_repo.save(workflow_configuration)
    workflow_configuration_repo.save(workflow_configuration_1)
    workflow_configuration_repo.save(workflow_configuration_2)

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration.tenant_id, document_type_id=workflow_configuration.document_type_id
        )
        == workflow_configuration
    )

    workflow_configuration_repo.delete(
        tenant_id=workflow_configuration.tenant_id, document_type_id=workflow_configuration.document_type_id
    )

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration.tenant_id, document_type_id=workflow_configuration.document_type_id
        )
        is None
    )

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration_1.tenant_id, document_type_id=workflow_configuration_1.document_type_id
        )
        == workflow_configuration_1
    )

    assert (
        workflow_configuration_repo.find(
            tenant_id=workflow_configuration_2.tenant_id, document_type_id=workflow_configuration_2.document_type_id
        )
        == workflow_configuration_2
    )
