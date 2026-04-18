from random import choice, randint
from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import (
    DocumentProcessingInfo,
    ExtractionType,
    WorkflowConfiguration,
)
from deps_workflow_manager.messaging.sagas_data import DocumentProcessingSteps
from tests.fakes import (
    FakeDocumentProcessingInfoRepository,
    FakeWorkflowConfigurationRepository,
)


@pytest.fixture
def entity_id():
    return uuid4().hex


@pytest.fixture
def document_id():
    return randint(1, 10)


@pytest.fixture
def document_name():
    return uuid4().hex


@pytest.fixture
def engine():
    return uuid4().hex


@pytest.fixture
def language():
    return uuid4().hex


@pytest.fixture
def llm_type():
    return uuid4().hex


@pytest.fixture
def files():
    return [uuid4().hex]


@pytest.fixture
def assign_to_me():
    return choice([True, False])


@pytest.fixture
def needs_unifier():
    return choice([True, False])


@pytest.fixture
def needs_extraction():
    return choice([True, False])


@pytest.fixture
def classification_enabled():
    return choice([True, False])


@pytest.fixture
def version_classification_enabled():
    return choice([True, False])


@pytest.fixture
def parsing_features():
    return {"text", "tables", "kvps"}


@pytest.fixture
def output_profile_ids():
    return [uuid4().hex, uuid4().hex]


@pytest.fixture
def document_metadata():
    return {"extension": "jpeg"}


@pytest.fixture
def exceptional_queue_enabled():
    return choice([True, False])


@pytest.fixture
def needs_user_verification():
    return choice([True, False])


@pytest.fixture
def workflow_configuration(tenant_id, document_type_id):
    wc = WorkflowConfiguration(tenant_id, document_type_id)
    wc.extraction_type = ExtractionType.PLUGIN
    return wc


@pytest.fixture
def document_processing_info(entity_id, tenant_id, parsing_features) -> DocumentProcessingInfo:
    return DocumentProcessingInfo(
        document_id=entity_id,
        tenant_id=tenant_id,
        needs_unifier=choice([True, False]),
        needs_extraction=choice([True, False]),
        assign_to_me=choice([True, False]),
        parsing_features=parsing_features,
    )


@pytest.fixture
def document_type_id():
    return uuid4().hex


@pytest.fixture
def fake_workflow_configuration_repository(tenant_id, document_type_id, workflow_configuration):
    return FakeWorkflowConfigurationRepository({(tenant_id, document_type_id): workflow_configuration})


@pytest.fixture
def fake_document_processing_info_repository(tenant_id, document_id, document_processing_info):
    return FakeDocumentProcessingInfoRepository({(tenant_id, document_id): document_processing_info})


@pytest.fixture
def pipeline_service(containers, fake_document_processing_info_repository):
    containers.reset_singletons()
    containers.repositories.document_processing.override(fake_document_processing_info_repository)
    yield containers.pipeline_service()


@pytest.fixture
def document_processing_saga_steps(pipeline_service, fake_workflow_configuration_repository):
    return DocumentProcessingSteps(fake_workflow_configuration_repository, pipeline_service)
