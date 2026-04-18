import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.domain.model import ErrorType, Status
from deps_workflow_manager.messaging.commands import (
    AssignDocumentType,
    AssignDocumentTypeReply,
    PerformClassification,
    PerformClassificationReply,
    PerformContainerUnificationReply,
    PerformParsing,
    PerformParsingReply,
    PerformPreprocess,
    PerformUnification,
    PerformUnificationReply,
    StartAttachmentsProcessing,
    StartDocumentProcessing,
    UpdateContainerData,
    UpdateDocumentState,
)
from deps_workflow_manager.messaging.sagas import TypelessDocumentProcessingSaga
from deps_workflow_manager.messaging.sagas_data import (
    Destination,
    TypelessDocumentProcessingSagaData,
)


@pytest.mark.no_doc_type_processing
def test_only_unification(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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


@pytest.mark.no_doc_type_processing
def test_parsing_next(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_extraction=False,
        needs_unifier=True,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply()
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.PARSING.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
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


@pytest.mark.no_doc_type_processing
@pytest.mark.parametrize("parsing_features", [None, []])
def test_classification_next(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    needs_extraction,
    document_metadata,
    parsing_features,
    exceptional_queue_enabled,
    needs_user_verification,
    typeless_document_processing_saga_steps,
):
    document_type_id = "glamour"

    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_extraction=needs_extraction,
        needs_unifier=True,
        current_status=Status.UNIFICATION,
        classification_enabled=True,
        exceptional_queue_enabled=exceptional_queue_enabled,
        needs_user_verification=needs_user_verification,
        document_metadata=document_metadata,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply()
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.CLASSIFICATION.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(AssignDocumentType(document_id, document_type_id))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            StartDocumentProcessing(
                document_id=document_id,
                document_type_id=document_type_id,
                document_name=document_name,
                files=files,
                tenant_id=tenant_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                assign_to_me=assign_to_me,
                parsing_features=parsing_features,
                needs_unifier=True,
                needs_extraction=needs_extraction,
                document_metadata=document_metadata,
                from_step=Status.UNIFICATION.value,
            )
        )
        .to(Destination.WORKFLOW_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )

    saga_data = suts.saga_data

    assert Status.UNIFICATION == Status(saga_data["current_status"])
    assert saga_data["needs_extraction"] == needs_extraction
    assert saga_data["needs_unifier"] == True
    assert saga_data["parsing_features"] == None
    assert saga_data["document_metadata"] == document_metadata
    assert saga_data["assign_to_me"] == assign_to_me
    assert saga_data["language"] == language
    assert saga_data["engine"] == engine
    assert saga_data["llm_type"] == llm_type
    assert saga_data["document_type_id"] is not None
    assert saga_data["document_id"] == document_id


@pytest.mark.no_doc_type_processing
def test_parsing_and_classification_next(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    needs_extraction,
    document_metadata,
    parsing_features,
    typeless_document_processing_saga_steps,
):
    document_type_id = "glamour"

    sd = TypelessDocumentProcessingSagaData(
        document_name=document_name,
        tenant_id=tenant_id,
        document_type_id=None,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        files=files,
        assign_to_me=assign_to_me,
        document_id=document_id,
        needs_extraction=needs_extraction,
        needs_unifier=True,
        current_status=Status.UNIFICATION,
        classification_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply()
        .command(
            UpdateDocumentState(
                document_id,
                Status.PARSING.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            PerformParsing(
                tenant_id=tenant_id,
                document_id=document_id,
                files=files,
                engine=engine,
                features=parsing_features,
            ),
        )
        .to(Destination.PARSING_SERVICE)
        .and_given()
        .success_reply(PerformParsingReply())
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.CLASSIFICATION.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(AssignDocumentType(document_id, document_type_id))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(
            StartDocumentProcessing(
                document_id=document_id,
                document_type_id=document_type_id,
                document_name=document_name,
                files=files,
                tenant_id=tenant_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                assign_to_me=assign_to_me,
                parsing_features=parsing_features,
                needs_unifier=True,
                needs_extraction=needs_extraction,
                document_metadata=document_metadata,
                from_step=Status.UNIFICATION.value,
            )
        )
        .to(Destination.WORKFLOW_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )

    saga_data = suts.saga_data
    assert Status.UNIFICATION == Status(saga_data["current_status"])


@pytest.mark.no_doc_type_processing
def test_classification_next__assign_doc_type_fails__start_doc_processing_doesnt_start(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    needs_extraction,
    typeless_document_processing_saga_steps,
):
    document_type_id = "glamour"

    sd = TypelessDocumentProcessingSagaData(
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
        needs_extraction=needs_extraction,
        needs_unifier=True,
        current_status=Status.UNIFICATION,
        classification_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply()
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.CLASSIFICATION.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect()
        .command(PerformClassification(document_id))
        .to(Destination.CLASSIFICATION_SERVICE)
        .and_given()
        .success_reply(
            PerformClassificationReply(document_type_id=document_type_id, error_type=None, error_message=None)
        )
        .expect()
        .command(AssignDocumentType(document_id, document_type_id))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply(AssignDocumentTypeReply(error_type=ErrorType.SYSTEM.value, error_message="test_error_message"))
        .expect()
        .command(UpdateDocumentState(document_id, Status.FAILURE.value))
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )

    saga_data = suts.saga_data
    assert Status.FAILURE == Status(saga_data["current_status"])


@pytest.mark.no_doc_type_processing
def test_image_preprocessing_next(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    sd = TypelessDocumentProcessingSagaData(
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
        needs_extraction=False,
        needs_unifier=True,
        needs_image_preprocessing=True,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .expect()
        .command(PerformPreprocess(document_id))
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


@pytest.mark.no_doc_type_processing
def test_system_error(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    error_message = "Unification service is sick today."
    sd = TypelessDocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply(PerformUnificationReply(ErrorType.SYSTEM.value, error_message))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.FAILURE.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.FAILURE == Status(saga_data["current_status"])
    assert ErrorType.SYSTEM == ErrorType(saga_data["error_type"])
    assert error_message == saga_data["error_message"]


@pytest.mark.no_doc_type_processing
def test_business_error(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    error_message = "Document smells like a bad mud."
    sd = TypelessDocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply(PerformUnificationReply(ErrorType.BUSINESS.value, error_message))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.POSTPONED.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.POSTPONED == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS == ErrorType(saga_data["error_type"])
    assert error_message == saga_data["error_message"]


@pytest.mark.no_doc_type_processing
def test_business_error_exceptional_queue_enabled(
    document_id,
    document_name,
    tenant_id,
    engine,
    language,
    llm_type,
    files,
    assign_to_me,
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    error_message = "Document smells like a bad mud."
    sd = TypelessDocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
        exceptional_queue_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
        .success_reply(PerformUnificationReply(ErrorType.BUSINESS.value, error_message))
        .expect()
        .command(
            UpdateDocumentState(
                document_id,
                Status.EXCEPTIONAL_QUEUE.value,
            )
        )
        .to(Destination.DOCUMENT_SERVICE)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert Status.EXCEPTIONAL_QUEUE == Status(saga_data["current_status"])
    assert ErrorType.BUSINESS == ErrorType(saga_data["error_type"])
    assert error_message == saga_data["error_message"]


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
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    container_data = dict(
        container_type="email",
        container_metadata={"metadata": "I'm a metadata"},
        attachments=[{"title": "test_title", "blob_name": "test_blob_name"}],
    )
    sd = TypelessDocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
        exceptional_queue_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
    typeless_document_processing_saga_steps,
):
    document_type_id = None
    container_data = dict(
        container_type="email",
        container_metadata={"metadata": "I'm a metadata"},
        attachments=[{"title": "test_title", "blob_name": "test_blob_name"}],
    )
    sd = TypelessDocumentProcessingSagaData(
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
        needs_unifier=True,
        needs_extraction=False,
        classification_enabled=False,
        current_status=Status.UNIFICATION,
        exceptional_queue_enabled=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            TypelessDocumentProcessingSaga(
                typeless_document_processing_saga_steps,
            ),
            sd,
        )
        .expect()
        .command(UpdateDocumentState(document_id, Status.UNIFICATION.value))
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
                container_type="email",
                container_metadata={"metadata": "I'm a metadata"},
                attachments=[],
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
