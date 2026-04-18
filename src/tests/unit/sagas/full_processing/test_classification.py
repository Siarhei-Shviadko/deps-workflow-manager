from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import Error, ErrorType, ExtractionType, Status
from deps_workflow_manager.messaging.commands import (
    PerformClassification,
    PerformClassificationReply,
    PerformExtraction,
    PerformParsing,
    PerformParsingReply,
    PerformPreprocess,
    PerformTemplateExtraction,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import FullProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    FullProcessingSagaData,
)


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_only_classification(
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
    workflow_configuration,
):
    workflow_configuration.parsing_features = set()
    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
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
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.classification_step
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
    workflow_configuration,
):
    error_message = uuid4().hex
    workflow_configuration.parsing_features = set()
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
                None,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(
                document_type_id=None,
                error_type=ErrorType.SYSTEM.value,
                error_message=error_message,
            )
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value, Error(ErrorType.SYSTEM, error_message)))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_exceptional_queue(
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
    workflow_configuration,
):
    error_message = "Document cannot be classified."
    workflow_configuration.invoke_parsing = False
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
                None,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                needs_exceptional_queue=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(
                document_type_id=None, error_type=ErrorType.BUSINESS.value, error_message=error_message
            )
        )
        .expect()
        .command(
            UpdateDocumentState(document_id, Status.EXCEPTIONAL_QUEUE.value, Error(ErrorType.BUSINESS, error_message)),
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS.value == saga_data["error_type"]
    assert error_message == saga_data["error_message"]


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_postponed(
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
    error_message = "Document cannot be classified."
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
                None,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                needs_exceptional_queue=False,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(
                document_type_id=None, error_type=ErrorType.BUSINESS.value, error_message=error_message
            )
        )
        .expect()
        .command(
            UpdateDocumentState(document_id, Status.POSTPONED.value, Error(ErrorType.BUSINESS, error_message)),
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


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_image_preprocessing_next__plugin(
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
    workflow_configuration.extraction_type = ExtractionType.PLUGIN
    workflow_configuration.image_transformations = {uuid4().hex}
    workflow_configuration.parsing_features = set()
    workflow_configuration.needs_user_verification = False
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
                None,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.IMAGE_PREPROCESSING.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformPreprocess(document_id, image_transformations=workflow_configuration.image_transformations))
        .to(Destination.IMAGE_PREPROCESS_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_image_preprocessing_next__template(
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
    workflow_configuration.extraction_type = ExtractionType.TEMPLATE
    workflow_configuration.parsing_features = set()
    workflow_configuration.needs_user_verification = False
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
                None,
                None,
                files,
                assign_to_me,
                document_id=document_id,
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.IMAGE_PREPROCESSING.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformPreprocess(document_id, image_transformations=workflow_configuration.image_transformations))
        .to(Destination.IMAGE_PREPROCESS_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformTemplateExtraction(
                tenant_id=tenant_id,
                document_id=int(document_id),
                template_id=document_type_id,
                language=language,
                engine=engine,
            )
        )
        .to(Destination.TEMPLATE_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.classification_step
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
    workflow_configuration,
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
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_image_preprocessing=False,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
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

    assert document_type_id == saga_data["document_type_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_extraction_next__plugin(
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
    workflow_configuration,
):
    workflow_configuration.extraction_type = ExtractionType.PLUGIN
    workflow_configuration.parsing_features = set()
    workflow_configuration.needs_user_verification = False
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
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformExtraction(document_id, document_type_id, language, engine))
        .to(Destination.EXTRACTION_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.classification_step
def test_extraction_next__template(
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
    workflow_configuration,
):
    workflow_configuration.extraction_type = ExtractionType.TEMPLATE
    workflow_configuration.parsing_features = set()
    workflow_configuration.needs_user_verification = False
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
                current_status=Status.CLASSIFICATION,
                invoke_classification=True,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.IMAGE_PREPROCESSING.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformPreprocess(document_id, image_transformations=workflow_configuration.image_transformations))
        .to(Destination.IMAGE_PREPROCESS_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.EXTRACTION.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformTemplateExtraction(
                tenant_id=tenant_id,
                document_id=int(document_id),
                template_id=document_type_id,
                language=language,
                engine=engine,
            )
        )
        .to(Destination.TEMPLATE_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert document_type_id == saga_data["document_type_id"]
    assert Status.COMPLETED == Status(saga_data["current_status"])
