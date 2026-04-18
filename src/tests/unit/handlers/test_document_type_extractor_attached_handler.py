from deps_workflow_manager.domain.model import ExtractionType
from deps_workflow_manager.messaging.handlers import (
    document_type_extractor_attached_handler,
)


def test_document_type_extractor_attached_handler__successful_command__configuration_saved(
    workflow_configuration_repository,
    extractor_attached_dee,
    test_tenant,
    document_type_id,
    extraction_type,
    image_transformations,
    engine,
):
    document_type_extractor_attached_handler(extractor_attached_dee)

    configuration = workflow_configuration_repository.find(test_tenant, document_type_id)

    assert configuration is not None
    assert configuration.tenant_id == test_tenant
    assert configuration.document_type_id == document_type_id
    assert configuration.extraction_type == ExtractionType(extraction_type)
    assert configuration.image_transformations == set(image_transformations)
    assert configuration.engine == engine
