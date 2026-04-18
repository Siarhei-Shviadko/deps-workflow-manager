import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    PerformClassification,
    PerformClassificationReply,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import FullProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    FullProcessingSagaData,
)


@pytest.mark.workflow_config
def test_config_is_not_found(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    fake_workflow_configuration_repository,
    full_processing_saga_steps,
):
    fake_workflow_configuration_repository.db = {}
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
                document_name,
                tenant_id,
                None,
                engine,
                language,
                llm_type,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM.value == saga_data["error_type"]
    assert "There is no workflow config for the document type." == saga_data["error_message"]


@pytest.mark.workflow_config
def test_extraction_plugin_is_not_set(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    workflow_configuration,
    full_processing_saga_steps,
):
    workflow_configuration.extraction_type = None
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
                document_name,
                tenant_id,
                None,
                engine,
                language,
                llm_type,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM.value == saga_data["error_type"]
    assert "There is no extraction capability for the document type." == saga_data["error_message"]
