import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import Status
from deps_workflow_manager.messaging.commands import (
    CreateDocument,
    CreateDocumentReply,
    PerformUnification,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import TypelessDocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    TypelessDocumentProcessingSagaData,
)


@pytest.mark.no_doc_type_processing
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
    document_metadata,
    typeless_document_processing_saga_steps,
):
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        parsing_features=None,
        llm_type=llm_type,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=False,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
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
        .command(
            UpdateDocumentState(
                document_id,
                Status.COMPLETED.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.no_doc_type_processing
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
    document_metadata,
    typeless_document_processing_saga_steps,
):
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_extraction=False,
        needs_unifier=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
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
        .command(
            UpdateDocumentState(
                document_id,
                Status.UNIFICATION.value,
            )
        )
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
