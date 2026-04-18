from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ExtractionType, Status
from deps_workflow_manager.messaging.commands import (
    PerformExporting,
    PerformExtraction,
    PerformParsing,
    PerformPostprocessing,
    PerformPreprocess,
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
def test_only_image_preprocessing(
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
        current_status=Status.IMAGE_PREPROCESSING,
        needs_unifier=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
    workflow_configuration,
):
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.IMAGE_PREPROCESSING,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
def test_extraction_with_version_classification_next(
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
    workflow_configuration.extraction_type = ExtractionType.TEMPLATE
    template_version_id = uuid4().hex
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
        current_status=Status.IMAGE_PREPROCESSING,
        needs_unifier=False,
        needs_parsing=False,
        needs_extraction=True,
        version_classification_enabled=True,
        document_metadata=document_metadata,
        extraction_type=ExtractionType.TEMPLATE,
        needs_user_verification=False,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
        .command(UpdateDocumentState(document_id, Status.VERSION_CLASSIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformVersionClassification(
                document_id=document_id,
                files=files,
                template_id=document_type_id,
            )
        )
        .to(Destination.VERSION_CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformVersionClassificationReply(
                document_id=document_id,
                template_id=document_type_id,
                version_id=template_version_id,
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
                document_type_id=document_type_id,
                tenant_id=tenant_id,
                document_id=document_id,
                extra_data={"template_version_id": template_version_id},
                language=language,
                engine=engine,
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
    assert template_version_id == saga_data["template_version_id"]


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
    workflow_configuration,
):
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.IMAGE_PREPROCESSING,
        needs_unifier=False,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformExtraction(
                document_type_id=document_type_id,
                document_id=document_id,
                tenant_id=tenant_id,
                language=language,
                engine=engine,
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
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.IMAGE_PREPROCESSING,
        needs_unifier=False,
        needs_parsing=False,
        needs_extraction=False,
        needs_postprocessing=True,
        document_metadata=document_metadata,
    )
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentProcessingSaga(document_processing_saga_steps),
            saga_data,
        )
        .expect()
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
    workflow_configuration,
):
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.IMAGE_PREPROCESSING,
        needs_unifier=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
    workflow_configuration.image_transformations = {uuid4().hex}
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
        current_status=Status.IMAGE_PREPROCESSING,
        needs_unifier=False,
        needs_parsing=False,
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
        .command(UpdateDocumentState(document_id=document_id, state=Status.IMAGE_PREPROCESSING.value, error=None))
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
