import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import Status
from deps_workflow_manager.messaging.commands import (
    CreateDocument,
    CreateDocumentReply,
    PerformUnification,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import FullProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    FullProcessingSagaData,
)


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_only_uploading(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    full_processing_saga_steps,
    invoke_unifier,
    invoke_extraction,
    parsing_features,
    document_metadata,
):
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
                document_name,
                tenant_id,
                document_type_id,
                engine,
                language,
                llm_type,
                None,
                files,
                assign_to_me,
                invoke_unifier=False,
                document_metadata=document_metadata,
            ),
        )
        .expect()
        .command(
            CreateDocument(
                document_name,
                document_type_id,
                engine,
                language,
                files,
                assign_to_me,
                document_metadata,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply(CreateDocumentReply(document_id))
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_unification_next(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    full_processing_saga_steps,
    invoke_unifier,
    invoke_extraction,
    parsing_features,
    document_metadata,
):
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
                document_name,
                tenant_id,
                document_type_id,
                engine,
                language,
                llm_type,
                None,
                files,
                assign_to_me,
                invoke_unifier=True,
                invoke_extraction=False,
                document_metadata=document_metadata,
            ),
        )
        .expect()
        .command(
            CreateDocument(
                document_name,
                document_type_id,
                engine,
                language,
                files,
                assign_to_me,
                document_metadata,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply(CreateDocumentReply(document_id))
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])
