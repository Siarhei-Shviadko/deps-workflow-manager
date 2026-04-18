from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ExtractionType, Status
from deps_workflow_manager.messaging.commands import (
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
@pytest.mark.image_preprocessing_step
def test_only_image_preprocessing(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    full_processing_saga_steps,
    workflow_configuration,
):
    workflow_configuration.image_transformations = {uuid4().hex}
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
                current_status=Status.IMAGE_PREPROCESSING,
                invoke_image_preprocessing=True,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformPreprocess(document_id, image_transformations=workflow_configuration.image_transformations))
        .to(Destination.IMAGE_PREPROCESS_SERVICE)
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

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.image_preprocessing_step
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
    workflow_configuration,
):
    workflow_configuration.image_transformations = {uuid4().hex}
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
                parsing_features={"text": True},
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.IMAGE_PREPROCESSING,
                invoke_image_preprocessing=True,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(PerformPreprocess(document_id, image_transformations=workflow_configuration.image_transformations))
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
@pytest.mark.image_preprocessing_step
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
    workflow_configuration.image_transformations = {uuid4().hex}

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
                document_name=document_name,
                tenant_id=tenant_id,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                parsing_features=None,
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.IMAGE_PREPROCESSING,
                invoke_image_preprocessing=True,
                invoke_extraction=True,
            ),
        )
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

    assert Status.COMPLETED == Status(saga_data["current_status"])


@pytest.mark.processing_steps
@pytest.mark.image_preprocessing_step
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
    workflow_configuration.image_transformations = {uuid4().hex}

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            FullProcessingSaga(full_processing_saga_steps),
            FullProcessingSagaData(
                document_name=document_name,
                tenant_id=tenant_id,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                parsing_features=None,
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.IMAGE_PREPROCESSING,
                invoke_image_preprocessing=True,
                invoke_extraction=True,
            ),
        )
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

    assert Status.COMPLETED == Status(saga_data["current_status"])
