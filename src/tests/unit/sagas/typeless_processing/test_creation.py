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
def test_document_creation(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
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
        document_id=None,
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.NEW,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(
            CreateDocument(
                document_name=document_name,
                document_type_id=None,
                engine=engine,
                language=language,
                llm_type=llm_type,
                files=files,
                assign_to_me=assign_to_me,
                document_metadata=None,
                parent_id=None,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply(CreateDocumentReply(document_id=document_id))
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id,
                None,
                files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
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
    assert document_id == saga_data["document_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.no_doc_type_processing
def test_unification_status_with_unifier(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id,
                None,
                files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
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
    assert document_id == saga_data["document_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.no_doc_type_processing
def test_unification_status_without_unifier(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
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
        needs_unifier=False,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
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
    assert document_id == saga_data["document_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])
