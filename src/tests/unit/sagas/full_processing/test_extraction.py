from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    PerformExtraction,
    PerformExtractionReply,
    PerformPostprocessing,
    PerformValidation,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import FullProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    FullProcessingSagaData,
)


@pytest.mark.processing_steps
@pytest.mark.extraction_step
def test_only_extraction(
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
                current_status=Status.EXTRACTION,
            ),
        )
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply(PerformExtractionReply())
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
@pytest.mark.extraction_step
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
                current_status=Status.EXTRACTION,
            ),
        )
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply(PerformExtractionReply(error_type=ErrorType.SYSTEM.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.extraction_step
def test_postprocessing_next(
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
    workflow_configuration.needs_postprocessing = True

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
                current_status=Status.EXTRACTION,
            ),
        )
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply(PerformExtractionReply())
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPROCESSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformPostprocessing(document_id))
        .to(Destination.POSTPROCESSING_SERVICE)
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
@pytest.mark.extraction_step
def test_validation_next(
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
    workflow_configuration.needs_validation = True

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
                current_status=Status.EXTRACTION,
            ),
        )
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply(PerformExtractionReply())
        .expect()
        .command(UpdateDocumentState(document_id, Status.VALIDATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformValidation(document_id, document_type_id))
        .to(Destination.VALIDATION_SERVICE)
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
@pytest.mark.extraction_step
def test_manual_review_next(
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
    workflow_configuration.needs_user_verification = True

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
                current_status=Status.EXTRACTION,
            ),
        )
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply(PerformExtractionReply())
        .expect()
        .command(UpdateDocumentState(document_id, Status.NEEDS_REVIEW.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.NEEDS_REVIEW == Status(saga_data["current_status"])
