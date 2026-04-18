from random import randint
from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import (
    ErrorType,
    ExtractionType,
    Status,
    WorkflowConfiguration,
)
from deps_workflow_manager.messaging.sagas_data import FullProcessingSteps
from tests.fakes import FakeWorkflowConfigurationRepository


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
    return False


@pytest.fixture
def workflow_configuration(tenant_id, document_type_id):
    wc = WorkflowConfiguration(tenant_id, document_type_id)
    wc.extraction_type = ExtractionType.PLUGIN
    wc.needs_user_verification = False
    wc.parsing_features = set()

    return wc


@pytest.fixture
def fake_workflow_configuration_repository(tenant_id, document_type_id, workflow_configuration):
    return FakeWorkflowConfigurationRepository({(tenant_id, document_type_id): workflow_configuration})


@pytest.fixture
def full_processing_saga_steps(fake_workflow_configuration_repository):
    return FullProcessingSteps(fake_workflow_configuration_repository)


@pytest.fixture
def invoke_unifier():
    return False


@pytest.fixture
def invoke_extraction():
    return False


@pytest.fixture
def parsing_features():
    return {"text", "tables", "kvps"}


@pytest.fixture
def document_metadata():
    return {"extension": "jpeg"}
