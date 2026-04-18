import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    PerformExtraction,
    PerformParsing,
    PerformParsingReply,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import FullProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    FullProcessingSagaData,
)


@pytest.mark.processing_steps
@pytest.mark.parsing_step
def test_only_parsing__passed_features(
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
    workflow_configuration.parsing_features = {"kvps"}

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
                parsing_features={"tables"},
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.PARSING,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                features=["tables"],
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
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
@pytest.mark.parsing_step
def test_only_parsing__default_features(
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
    workflow_configuration.parsing_features = {"kvps"}

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
                current_status=Status.PARSING,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                features=["kvps"],
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
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
@pytest.mark.parsing_step
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
                parsing_features={"tables"},
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.PARSING,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                features=["tables"],
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply(error_type=ErrorType.SYSTEM.value, error_message="error_message"))
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
@pytest.mark.parsing_step
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
    full_processing_saga_steps,
):
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
                parsing_features={"tables"},
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.PARSING,
                invoke_extraction=True,
            ),
        )
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                features=["tables"],
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
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
@pytest.mark.parsing_step
def test_document_type_id_is_not_provided(
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
                document_name=document_name,
                tenant_id=tenant_id,
                document_type_id=None,
                engine=engine,
                language=language,
                llm_type=llm_type,
                parsing_features={"tables"},
                files=files,
                assign_to_me=assign_to_me,
                document_id=document_id,
                current_status=Status.PARSING,
                invoke_extraction=False,
            ),
        )
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                features=["tables"],
            )
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
        .expect()
        .command(UpdateDocumentState(document_id, Status.COMPLETED.value, None))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.COMPLETED == Status(saga_data["current_status"])
