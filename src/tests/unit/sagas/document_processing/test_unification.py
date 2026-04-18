from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, ExtractionType, Status
from deps_workflow_manager.messaging.commands import (
    PerformContainerUnificationReply,
    PerformExporting,
    PerformExtraction,
    PerformParsing,
    PerformPostprocessing,
    PerformPreprocess,
    PerformUnification,
    PerformUnificationReply,
    PerformVersionClassification,
    PerformVersionClassificationReply,
    StartAttachmentsProcessing,
    UpdateContainerData,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import DocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    DocumentProcessingSagaData,
)


@pytest.mark.document_processing
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
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
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


@pytest.mark.document_processing
def test_image_preprocessing_next(
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
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
        needs_image_preprocessing=True,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.IMAGE_PREPROCESSING.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformPreprocess(
                document_id=document_id,
            )
        )
        .to(Destination.IMAGE_PREPROCESS_SERVICE)
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_image_preprocessing=True,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
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
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                engine=engine,
                document_type_id=document_type_id,
                language=language,
                features=parsing_features,
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(PerformUnificationReply(error_type=ErrorType.SYSTEM.value, error_message=error_message))
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(PerformUnificationReply(error_type=ErrorType.BUSINESS.value, error_message=error_message))
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


@pytest.mark.document_processing
def test_error_exceptional_queue_enabled(
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        exceptional_queue_enabled=True,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
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


@pytest.mark.document_processing
def test_extraction_next(
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
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
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
                engine=engine,
                tenant_id=tenant_id,
                document_type_id=document_type_id,
                language=language,
            )
        )
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


@pytest.mark.document_processing
def test_extraction_with_image_preprocess(
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
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
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
        .command(
            PerformExtraction(
                document_id=document_id,
                engine=engine,
                tenant_id=tenant_id,
                document_type_id=document_type_id,
                language=language,
            )
        )
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


@pytest.mark.document_processing
def test_version_classification_enabled(
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
    workflow_configuration.extraction_type = ExtractionType.TEMPLATE
    version_id = uuid4().hex
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
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
        .command(UpdateDocumentState(document_id, Status.VERSION_CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformVersionClassification(
                document_id=document_id,
                template_id=document_type_id,
                files=files,
            )
        )
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
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExtraction(
                document_id=document_id,
                extra_data={"template_version_id": version_id},
                document_type_id=document_type_id,
                tenant_id=tenant_id,
                engine=engine,
                language=language,
            )
        )
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
    assert version_id == saga_data["template_version_id"]


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
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
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
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.document_processing
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
    document_processing_saga_steps,
    document_metadata,
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
        parsing_features=None,
        output_profile_ids=None,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
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
        current_status=Status.UNIFICATION,
        needs_unifier=True,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id=document_id,
                document_type_id=document_type_id,
                files=files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
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
        .command(UpdateDocumentState(document_id, Status.EXPORTED.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXPORTED == Status(saga_data["current_status"])


@pytest.mark.container_type_doc
def test_only_unification__container_doc_type__with_attachments__goes_to_completed_state(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_processing_saga_steps,
    document_type_id,
):
    container_data = dict(
        container_type="email",
        container_metadata={"metadata": "I'm a metadata"},
        attachments=[{"title": "test_title", "blob_name": "test_blob_name"}],
    )
    sd = DocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        current_status=Status.UNIFICATION,
        exceptional_queue_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id,
                document_type_id,
                files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(
            PerformContainerUnificationReply(
                container_type=container_data["container_type"],
                container_metadata=container_data["container_metadata"],
                attachments=container_data["attachments"],
                error_message=None,
                error_type=None,
            )
        )
        .expect()
        .command(
            UpdateContainerData(
                document_id=document_id,
                container_type=container_data["container_type"],
                container_metadata=container_data["container_metadata"],
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            StartAttachmentsProcessing(
                documents=container_data["attachments"],
                tenant_id=tenant_id,
                parent_id=document_id,
                engine=engine,
                language=language,
                assign_to_me=assign_to_me,
                parsing_features=None,
                needs_unifier=True,
                needs_extraction=False,
            )
        )
        .to(Destination.WORKFLOW_SERVICE)
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

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.container_type_doc
def test_only_unification__container_doc_type__no_attachments__goes_to_completed_state(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    document_processing_saga_steps,
    document_type_id,
):
    container_data = dict(container_type="email", container_metadata={"metadata": "I'm a metadata"}, attachments=[])
    sd = DocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        current_status=Status.UNIFICATION,
        exceptional_queue_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.UNIFICATION.value, error=None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformUnification(
                document_id,
                document_type_id,
                files,
            )
        )
        .to(Destination.UNIFIER_SERVICE)
        .and_given()
        .success_reply(
            PerformContainerUnificationReply(
                container_type=container_data["container_type"],
                container_metadata=container_data["container_metadata"],
                attachments=container_data["attachments"],
                error_message=None,
                error_type=None,
            )
        )
        .expect()
        .command(
            UpdateContainerData(
                document_id=document_id,
                container_type=container_data["container_type"],
                container_metadata=container_data["container_metadata"],
            )
        )
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

    assert Status.COMPLETED == Status(saga_data["current_status"])
