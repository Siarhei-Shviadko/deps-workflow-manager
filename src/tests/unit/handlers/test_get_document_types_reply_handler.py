from deps_workflow_manager.domain.model import (
    ExtractionType,
    IWorkflowConfigurationRepository,
)
from deps_workflow_manager.messaging.handlers import get_document_types_reply_handler


def test_get_document_types_reply_handler__successful_command__configuration_saved(
    workflow_configuration_repository: IWorkflowConfigurationRepository,
    get_document_types_reply_cm,
    tenant_id,
    document_type_id,
    extraction_type,
    image_transformations,
    llm_type,
    engine,
):
    get_document_types_reply_handler(get_document_types_reply_cm)

    configuration = workflow_configuration_repository.find(tenant_id, document_type_id)

    assert configuration is not None
    assert configuration.tenant_id == tenant_id
    assert configuration.document_type_id == document_type_id
    assert configuration.extraction_type == ExtractionType(extraction_type)
    assert configuration.image_transformations == set(image_transformations)
    assert configuration.llm_type == llm_type
    assert configuration.engine == engine


def test_get_document_types_reply_handler__failed_command__no_error(failed_get_document_types_reply_cm):
    get_document_types_reply_handler(failed_get_document_types_reply_cm)
