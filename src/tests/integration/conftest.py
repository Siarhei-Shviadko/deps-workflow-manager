import json
from random import choice
from uuid import uuid4

import pytest
from deps_message_flow.sagas.orchestration import (
    SagaData,
    SagaInstance,
    SerializedSagaData,
)

from deps_workflow_manager.domain.model import (
    DocumentProcessingInfo,
    ExtractionType,
    ParsingFeature,
    WorkflowConfiguration,
)


@pytest.fixture(autouse=True)
def session(containers):
    database = containers.datasources.postgres_datasource()
    connection = database.get_connection()

    class TrapForThreadLocalConnections:
        """
        This class is used instead of threading.local in Database, for allowing connection transactions management
        """

        connection = None
        transaction = None

    transaction = connection.begin_nested()
    TrapForThreadLocalConnections.connection = connection
    TrapForThreadLocalConnections.transaction = transaction
    database._registry = TrapForThreadLocalConnections

    try:
        yield
    finally:
        transaction.rollback()
    database.close()


@pytest.fixture
def saga_instance_repo(repositories):
    yield repositories.saga_instance()


@pytest.fixture
def workflow_configuration_repo(repositories):
    yield repositories.workflow_configuration()


@pytest.fixture
def document_processing_info_repo(repositories):
    yield repositories.document_processing()


@pytest.fixture
def workflow_state_service(containers):
    yield containers.workflow_state_service()


@pytest.fixture
def workflow_configuration_service(containers):
    yield containers.workflow_configuration_service()


@pytest.fixture
def entity_id():
    return uuid4().hex


@pytest.fixture
def serialized_saga_data(entity_id):
    return SerializedSagaData(saga_data_type=SagaData.__name__, saga_data_json=json.dumps({"entity_id": entity_id}))


@pytest.fixture
def saga_instance(serialized_saga_data):
    return SagaInstance(
        saga_type="Test",
        saga_id="None",
        state_name="????",
        last_request_id="None",
        serialized_saga_data=serialized_saga_data,
    )


@pytest.fixture
def workflow_configuration(tenant_id, document_type_id):
    return WorkflowConfiguration(
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        image_transformations={"transf_1", "transf_2"},
        extraction_type=ExtractionType.PLUGIN,
        needs_postprocessing=True,
        needs_validation=True,
        needs_user_verification=False,
        needs_output_exporting=True,
        needs_review_on_validation_failure=True,
        llm_type="gpt-4",
        engine="tesseract",
    )


@pytest.fixture
def parsing_features():
    return choice(
        [
            None,
            {ParsingFeature.TEXT, ParsingFeature.KEY_VALUE_PAIRS},
            {ParsingFeature.TABLES, ParsingFeature.IMAGES, ParsingFeature.TEXT},
        ]
    )


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
def saved_document_processing_info(document_processing_info_repo, document_processing_info) -> DocumentProcessingInfo:
    document_processing_info_repo.save(document_processing_info)
    return document_processing_info
