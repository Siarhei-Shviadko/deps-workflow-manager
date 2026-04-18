from random import choice, randint
from uuid import uuid4

import pytest

from deps_workflow_manager.messaging.sagas_data import TypelessDocumentProcessingSteps
from tests.fakes import FakeDocumentProcessingInfoRepository


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
def document_metadata():
    return {"extension": "jpeg"}


@pytest.fixture
def exceptional_queue_enabled():
    return choice([True, False])


@pytest.fixture
def needs_user_verification():
    return choice([True, False])


@pytest.fixture
def pipeline_service(containers):
    containers.reset_singletons()
    containers.repositories.document_processing.override(FakeDocumentProcessingInfoRepository())
    yield containers.pipeline_service()


@pytest.fixture
def typeless_document_processing_saga_steps(pipeline_service):
    return TypelessDocumentProcessingSteps(pipeline_service)
