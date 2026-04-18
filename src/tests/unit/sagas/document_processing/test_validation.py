import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import Status
from deps_workflow_manager.messaging.commands import (
    PerformExporting,
    PerformValidation,
    PerformValidationReply,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import DocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    DocumentProcessingSagaData,
)


@pytest.mark.document_processing
def test_only_validation(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_processing_saga_steps,
    document_metadata,
    workflow_configuration,
):
    workflow_configuration.needs_validation = True
    workflow_configuration.needs_user_verification = False
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.VALIDATION,
        needs_unifier=False,
        needs_extraction=True,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.VALIDATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformValidation(document_id=document_id, document_type_id=document_type_id))
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


@pytest.mark.document_processing
def test_manual_review_next__needs_review_if_required_on_validation_failure(
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
    fake_workflow_configuration_repository,
    document_processing_saga_steps,
    document_metadata,
):
    workflow_configuration.needs_validation = True
    workflow_configuration.needs_review_on_validation_failure = True

    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.VALIDATION,
        needs_unifier=False,
        needs_extraction=True,
        document_metadata=document_metadata,
        needs_review_on_validation_failure=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformValidation(document_id=document_id, document_type_id=document_type_id))
        .to(Destination.VALIDATION_SERVICE)
        .and_given()
        .success_reply(PerformValidationReply(result=False))
        .expect()
        .command(UpdateDocumentState(document_id, Status.NEEDS_REVIEW.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.NEEDS_REVIEW == Status(saga_data["current_status"])


@pytest.mark.document_processing
def test_manual_review_next__needs_review_if_needs_user_verification(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_processing_saga_steps,
    document_metadata,
    workflow_configuration,
):
    workflow_configuration.needs_validation = True
    workflow_configuration.needs_user_verification = True
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.VALIDATION,
        needs_unifier=False,
        needs_extraction=True,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformValidation(document_id=document_id, document_type_id=document_type_id))
        .to(Destination.VALIDATION_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.NEEDS_REVIEW.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.NEEDS_REVIEW == Status(saga_data["current_status"])


@pytest.mark.document_processing
def test_exporting_next(
    document_id,
    document_name,
    tenant_id,
    document_type_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_processing_saga_steps,
    document_metadata,
    workflow_configuration,
):
    workflow_configuration.needs_validation = True
    workflow_configuration.needs_output_exporting = True
    workflow_configuration.needs_user_verification = False
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.VALIDATION,
        needs_unifier=False,
        needs_extraction=True,
        document_metadata=document_metadata,
        needs_output_exporting=True,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformValidation(document_id=document_id, document_type_id=document_type_id))
        .to(Destination.VALIDATION_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXPORTING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformExporting(document_id=document_id, document_type_id=document_type_id, profile_ids=None))
        .to(Destination.EXPORTING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXPORTED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXPORTED == Status(saga_data["current_status"])
