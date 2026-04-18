import pytest

from deps_workflow_manager.domain.model import WorkflowConfiguration
from deps_workflow_manager.messaging.handlers import document_type_updated_handler


@pytest.mark.usefixtures("save_workflow_configuration")
def test_document_type_updated_handler__configuration_updated(
    workflow_configuration_repository,
    document_type_updated_dee,
    test_tenant,
    document_type_id,
    llm_type,
    engine,
):
    document_type_updated_handler(document_type_updated_dee)

    configuration = workflow_configuration_repository.find(test_tenant, document_type_id)

    assert configuration is not None
    assert configuration.tenant_id == test_tenant
    assert configuration.document_type_id == document_type_id
    assert configuration.llm_type == llm_type
    assert configuration.engine == engine
