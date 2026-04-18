from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    PerformClassification,
    PerformExtraction,
    PerformParsing,
    PerformParsingReply,
    PerformPreprocess,
    PerformUnification,
    PerformUnificationReply,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import FullProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    FullProcessingSagaData,
)


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_only_unification(
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
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_extraction=False,
            ),
        )
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


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_parsing_next(
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
                {"text"},
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
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
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                features=["text"],
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
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
@pytest.mark.unification_step
def test_system_error(
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
):
    error_message = uuid4().hex
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
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(PerformUnificationReply(ErrorType.SYSTEM.value, error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM == ErrorType(saga_data["error_type"])
    assert error_message == saga_data["error_message"]


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_unsupported_file_format(
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
):
    error_message = uuid4().hex
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
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                needs_exceptional_queue=True,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(PerformUnificationReply(ErrorType.BUSINESS.value, error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXCEPTIONAL_QUEUE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS == ErrorType(saga_data["error_type"])
    assert error_message == saga_data["error_message"]


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_unsupported_file_format_without_exceptional_queue(
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
):
    error_message = uuid4().hex
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
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                needs_exceptional_queue=False,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(PerformUnificationReply(ErrorType.BUSINESS.value, error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPONED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS == ErrorType(saga_data["error_type"])
    assert error_message == saga_data["error_message"]


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_document_type_is_provided_without_image_preprocessing(
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
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
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


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_document_type_is_provided_with_image_preprocessing(
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
    workflow_configuration.image_transformations = {uuid4().hex}
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
                document_id=document_id,
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.IMAGE_PREPROCESSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformPreprocess(document_id))
        .to(Destination.IMAGE_PREPROCESS_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
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


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_document_type_is_not_provided(
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
):
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
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_classification=True,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
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


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_document_type_is_not_provided_exceptional_queue(
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
):
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
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_classification=False,
                invoke_extraction=True,
                needs_exceptional_queue=True,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXCEPTIONAL_QUEUE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])

    assert ErrorType.BUSINESS == ErrorType(saga_data["error_type"])
    assert "Document type is not provided." == saga_data["error_message"]


@pytest.mark.processing_steps
@pytest.mark.unification_step
def test_document_type_is_not_provided_postponed(
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
):
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
                current_status=Status.UNIFICATION,
                invoke_unifier=True,
                invoke_classification=False,
                invoke_extraction=True,
                needs_exceptional_queue=False,
            ),
        )
        .expect()
        .command(PerformUnification(document_id, document_type_id, files))
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPONED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])

    assert ErrorType.BUSINESS == ErrorType(saga_data["error_type"])
    assert "Document type is not provided." == saga_data["error_message"]
