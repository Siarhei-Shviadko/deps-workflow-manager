import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    AssignDocumentType,
    PerformClassification,
    PerformClassificationReply,
    PerformParsing,
    PerformParsingReply,
    StartDocumentProcessing,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import TypelessDocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    TypelessDocumentProcessingSagaData,
)


@pytest.mark.no_doc_type_processing
def test_only_pasing(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=False,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.PARSING,
        needs_image_preprocessing=False,
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
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
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
@pytest.mark.parametrize(
    "parsing_features", [{"tables"}, {"kvps"}, {"text"}, {"tables", "text"}, {"kvps", "text"}, {"text", "tables"}]
)
def test_only_pasing_with_some_features(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=False,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.PARSING,
        needs_image_preprocessing=False,
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
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
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
def test_test_system_error(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=False,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.PARSING,
        needs_image_preprocessing=False,
    )
    error_message = "error_message_test"
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(error_type=ErrorType.SYSTEM.value, error_message=error_message))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.FAILURE.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert saga_data["error_message"] == error_message
    assert saga_data["error_type"] == ErrorType.SYSTEM.value


@pytest.mark.no_doc_type_processing
def test_test_business_error(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=False,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.PARSING,
        needs_image_preprocessing=False,
    )
    error_message = "error_message_business"
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(error_type=ErrorType.BUSINESS.value, error_message=error_message))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.POSTPONED.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])
    assert saga_data["error_message"] == error_message
    assert saga_data["error_type"] == ErrorType.BUSINESS.value


@pytest.mark.no_doc_type_processing
def test_classification_next(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    parsing_features,
    needs_extraction,
    document_metadata,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_unifier=False,
        needs_extraction=needs_extraction,
        classification_enabled=True,
        current_status=Status.PARSING,
        needs_image_preprocessing=False,
        document_metadata=document_metadata,
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
        .command(UpdateDocumentState(document_id, Status.PARSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.CLASSIFICATION.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(PerformClassificationReply(document_type_id="Greak", error_type=None, error_message=None))
        .expect()
        .command(AssignDocumentType(document_id, document_type_id))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
                parsing_features=None,
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
    assert saga_data["needs_unifier"] == False
    assert set(saga_data["parsing_features"]) == set(parsing_features)
    assert saga_data["document_metadata"] == document_metadata
    assert saga_data["assign_to_me"] == assign_to_me
    assert saga_data["language"] == language
    assert saga_data["engine"] == engine
    assert saga_data["llm_type"] == llm_type
    assert saga_data["document_type_id"] is not None
    assert saga_data["document_id"] == document_id
