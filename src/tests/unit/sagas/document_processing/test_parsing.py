import json
from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, ExtractionType, Status
from deps_workflow_manager.messaging.commands import (
    PerformExporting,
    PerformExtraction,
    PerformParsing,
    PerformParsingReply,
    PerformPostprocessing,
    PerformVersionClassification,
    PerformVersionClassificationReply,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import DocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    DocumentProcessingSagaData,
)


@pytest.mark.document_processing
def test_only_parsing(
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
    parsing_features,
):
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        needs_user_verification=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
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
def test_needs_parsing_without_features__parsing_initiated_anyway(
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
):
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
        parsing_features=None,
        output_profile_ids=None,
        needs_parsing=True,
        needs_user_verification=False,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=None,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
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
def test_extraction_with_version_classification_enabled(
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
    parsing_features,
    workflow_configuration,
):
    workflow_configuration.extraction_type = ExtractionType.TEMPLATE
    version_id = uuid4().hex
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=True,
        version_classification_enabled=True,
        needs_user_verification=False,
        document_metadata=document_metadata,
        extraction_type=ExtractionType.TEMPLATE,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.VERSION_CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformVersionClassification(document_id=document_id, files=files, template_id=document_type_id))
        .to(Destination.VERSION_CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformVersionClassificationReply(
                document_id=document_id,
                template_id=document_type_id,
                version_id=version_id,
                error_type=None,
                error_message=None,
            )
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExtraction(
                document_type_id=document_type_id,
                tenant_id=tenant_id,
                document_id=document_id,
                extra_data={"template_version_id": version_id},
                language=language,
                engine=engine,
            )
        )
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])
    assert version_id == saga_data["template_version_id"]


@pytest.mark.document_processing
def test_extraction_with_plugin_next(
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
    parsing_features,
):
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=True,
        needs_user_verification=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExtraction(
                document_id=document_id,
                document_type_id=document_type_id,
                tenant_id=tenant_id,
                language=language,
                engine=engine,
            )
        )
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.document_processing
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
    document_processing_saga_steps,
    document_metadata,
    parsing_features,
    workflow_configuration,
):
    workflow_configuration.needs_postprocessing = True
    workflow_configuration.needs_user_verification = False
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPROCESSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformPostprocessing(
                document_id=document_id,
            )
        )
        .to(Destination.POSTPROCESSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.document_processing
def test_user_verification_next(
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
    parsing_features,
    workflow_configuration,
):
    workflow_configuration.needs_user_verification = True
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
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
    parsing_features,
    workflow_configuration,
):
    workflow_configuration.needs_output_exporting = True
    workflow_configuration.needs_user_verification = False
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        needs_output_exporting=True,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXPORTING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExporting(
                document_id=document_id,
                document_type_id=document_type_id,
                profile_ids=None,
            ),
        )
        .to(Destination.EXPORTING_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXPORTED))
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
    parsing_features,
):
    error_message = "system_error_message"
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(error_type=ErrorType.SYSTEM.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


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
    parsing_features,
):
    error_message = "business_error_message"
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        exceptional_queue_enabled=True,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(error_type=ErrorType.BUSINESS.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXCEPTIONAL_QUEUE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


@pytest.mark.document_processing
def test_business_error(
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
    parsing_features,
):
    error_message = "business_error_message"
    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        exceptional_queue_enabled=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                features=parsing_features,
                document_type_id=document_type_id,
                language=language,
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(error_type=ErrorType.BUSINESS.value, error_message=error_message))
        .expect()
        .command(UpdateDocumentState(document_id, Status.POSTPONED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


@pytest.mark.document_processing
def test_parsing_without_engine__engine_gotten_from_configuration(
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
    parsing_features,
    workflow_configuration,
):
    workflow_configuration.engine = engine

    saga_data = DocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=None,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.PARSING,
        needs_unifier=False,
        needs_extraction=False,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.PARSING.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
    )

    sent_payload = json.loads(suts._sent_commands[0].message.payload)
    assert sent_payload["engine"] == engine
