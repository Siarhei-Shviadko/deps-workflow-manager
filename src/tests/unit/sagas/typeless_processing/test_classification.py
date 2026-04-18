import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    AssignDocumentType,
    PerformClassification,
    PerformClassificationReply,
    StartDocumentProcessing,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import TypelessDocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    TypelessDocumentProcessingSagaData,
)


@pytest.mark.no_doc_type_processing
def test_classification__successful(
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
    needs_unifier,
    needs_extraction,
    typeless_document_processing_saga_steps,
):
    parsing_features = {"tables"}
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=needs_unifier,
        needs_extraction=needs_extraction,
        classification_enabled=True,
        current_status=Status.CLASSIFICATION,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformClassification(
                document_id,
            )
        )
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_message=None, error_type=None)
        )
        .expect()
        .command(AssignDocumentType(document_id, document_type_id))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
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
        .command(
            StartDocumentProcessing(
                document_id=document_id,
                document_type_id=document_type_id,
                document_name=document_name,
                tenant_id=tenant_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                assign_to_me=assign_to_me,
                files=files,
                parsing_features=parsing_features,
                needs_unifier=True,
                needs_extraction=needs_extraction,
                document_metadata=document_metadata,
                from_step=Status.UNIFICATION.value,
            )
        )
        .to(Destination.WORKFLOW_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data
    assert Status.UNIFICATION == Status(saga_data["current_status"])
    assert saga_data["needs_extraction"] == needs_extraction
    assert saga_data["needs_unifier"] == needs_unifier
    assert set(saga_data["parsing_features"]) == set(parsing_features)
    assert saga_data["document_metadata"] == document_metadata
    assert saga_data["assign_to_me"] == assign_to_me
    assert saga_data["language"] == language
    assert saga_data["engine"] == engine
    assert saga_data["llm_type"] == llm_type
    assert saga_data["document_type_id"] is not None
    assert saga_data["document_id"] == document_id


@pytest.mark.no_doc_type_processing
def test_classification_fails(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_metadata,
    needs_unifier,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    error_message = "I'm on vacation today."
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=needs_unifier,
        classification_enabled=True,
        current_status=Status.CLASSIFICATION,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformClassification(
                document_id,
            )
        )
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(
                document_type_id=None, error_type=ErrorType.SYSTEM.value, error_message=error_message
            )
        )
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.FAILURE.value,
                Error(ErrorType.SYSTEM, error_message),
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


@pytest.mark.no_doc_type_processing
def test_postponed(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_metadata,
    needs_unifier,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    error_message = "I don't like classifying docs."
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=needs_unifier,
        classification_enabled=True,
        current_status=Status.CLASSIFICATION,
        document_metadata=document_metadata,
        exceptional_queue_enabled=False,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformClassification(
                document_id,
            )
        )
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(
                document_type_id=None, error_type=ErrorType.BUSINESS.value, error_message=error_message
            )
        )
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.POSTPONED.value,
                Error(ErrorType.BUSINESS, error_message),
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


@pytest.mark.no_doc_type_processing
def test_classification__successful__next_steps__ok(
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
    needs_unifier,
    needs_extraction,
    typeless_document_processing_saga_steps,
):
    parsing_features = ["tables"]

    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=needs_unifier,
        needs_extraction=needs_extraction,
        classification_enabled=True,
        current_status=Status.CLASSIFICATION,
        document_metadata=document_metadata,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformClassification(
                document_id,
            )
        )
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(AssignDocumentType(document_id, document_type_id))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
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
        .command(
            StartDocumentProcessing(
                document_id=document_id,
                document_type_id=document_type_id,
                document_name=document_name,
                files=files,
                tenant_id=tenant_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                assign_to_me=assign_to_me,
                parsing_features=parsing_features,
                needs_unifier=needs_unifier,
                needs_extraction=needs_extraction,
                document_metadata=document_metadata,
                from_step=Status.UNIFICATION.value,
            )
        )
        .to(Destination.WORKFLOW_SERVICE)
    )
    saga_data = suts.saga_data

    assert Status.UNIFICATION == Status(saga_data["current_status"])
    assert saga_data["needs_extraction"] == needs_extraction
    assert saga_data["needs_unifier"] == needs_unifier
    assert set(saga_data["parsing_features"]) == set(parsing_features)
    assert saga_data["document_metadata"] == document_metadata
    assert saga_data["assign_to_me"] == assign_to_me
    assert saga_data["language"] == language
    assert saga_data["engine"] == engine
    assert saga_data["llm_type"] == llm_type
    assert saga_data["document_type_id"] is not None
    assert saga_data["document_id"] == document_id


@pytest.mark.no_doc_type_processing
def test_exceptional_queue(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_metadata,
    needs_unifier,
    needs_extraction,
    typeless_document_processing_saga_steps,
):
    parsing_features = {"tables"}
    error_message = "exceptiona_queue_error_message"
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=needs_unifier,
        needs_extraction=needs_extraction,
        classification_enabled=True,
        current_status=Status.CLASSIFICATION,
        document_metadata=document_metadata,
        exceptional_queue_enabled=True,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(typeless_document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformClassification(
                document_id,
            )
        )
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(
                document_type_id=None, error_type=ErrorType.BUSINESS.value, error_message=error_message
            )
        )
        .expect()
        .command(
            UpdateDocumentState(document_id, Status.EXCEPTIONAL_QUEUE.value, Error(ErrorType.BUSINESS, error_message))
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])
