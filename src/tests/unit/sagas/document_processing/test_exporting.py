import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    PerformExporting,
    PerformExportingReply,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import DocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    DocumentProcessingSagaData,
)


@pytest.mark.document_processing
def test_only_exporting(
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
    workflow_configuration,
    document_processing_saga_steps,
    output_profile_ids,
):
    workflow_configuration.needs_output_exporting = True
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=None,
        output_profile_ids=output_profile_ids,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.EXPORTING,
        needs_unifier=False,
        needs_extraction=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.EXPORTING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExporting(
                document_id=document_id,
                document_type_id=document_type_id,
                profile_ids=output_profile_ids,
            )
        )
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


@pytest.mark.document_processing
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
    document_processing_saga_steps,
    document_metadata,
    workflow_configuration,
):
    workflow_configuration.needs_output_exporting = True
    error_message = "system_error_message"
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
        current_status=Status.EXPORTING,
        needs_unifier=False,
        needs_extraction=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.EXPORTING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExporting(
                document_id=document_id,
                document_type_id=document_type_id,
                profile_ids=None,
            )
        )
        .to(Destination.EXPORTING_SERVICE)
        .and_given()
        .success_reply(PerformExportingReply(error_type=ErrorType.SYSTEM.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert error_message == saga_data["error_message"]
    assert ErrorType.SYSTEM.value == saga_data["error_type"]


@pytest.mark.document_processing
def test_business_error_exceptional_queue_enabled(
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
    workflow_configuration.needs_output_exporting = True
    error_message = "business_error_message"
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
        current_status=Status.EXPORTING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
        needs_output_exporting=True,
        exceptional_queue_enabled=True,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.EXPORTING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExporting(
                document_id=document_id,
                document_type_id=document_type_id,
                profile_ids=None,
            )
        )
        .to(Destination.EXPORTING_SERVICE)
        .and_given()
        .success_reply(PerformExportingReply(error_type=ErrorType.BUSINESS.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXCEPTIONAL_QUEUE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])
    assert error_message == saga_data["error_message"]
    assert ErrorType.BUSINESS.value == saga_data["error_type"]


@pytest.mark.document_processing
def test_business_error_exceptional_queue_disabled(
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
    workflow_configuration.needs_output_exporting = True
    error_message = "business_error_message"
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
        current_status=Status.EXPORTING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
        needs_output_exporting=True,
        exceptional_queue_enabled=False,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.EXPORTING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExporting(
                document_id=document_id,
                document_type_id=document_type_id,
                profile_ids=None,
            )
        )
        .to(Destination.EXPORTING_SERVICE)
        .and_given()
        .success_reply(PerformExportingReply(error_type=ErrorType.BUSINESS.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPONED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])
    assert error_message == saga_data["error_message"]
    assert ErrorType.BUSINESS.value == saga_data["error_type"]
