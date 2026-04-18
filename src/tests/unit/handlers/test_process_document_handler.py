from uuid import uuid4

from deps_message_flow.commands.consumer import CommandMessage

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.domain.model import NeedsReviewOption, ParsingFeature, Status
from deps_workflow_manager.messaging.commands import ProcessDocument
from deps_workflow_manager.messaging.handlers import process_document_handler


def test_process_document_handler(import_document_command_message, mocker):
    document_id = uuid4().hex
    tenant_id = uuid4().hex
    files = [uuid4().hex]
    document_type_id = uuid4().hex
    engine = uuid4().hex
    language = uuid4().hex
    llm_type = uuid4().hex
    parsing_features = ["text", "kvps"]
    needs_unification: bool = True
    needs_extraction: bool = True
    needs_parsing: bool = True
    needs_validation: bool = True
    needs_review: NeedsReviewOption = NeedsReviewOption.ALWAYS_REVIEW
    needs_output_exporting: bool = True

    process_document = mocker.patch.object(DocumentProcessingService, "process_document")

    command_message = mocker.Mock(CommandMessage)
    command_message.command = ProcessDocument(
        document_id=document_id,
        tenant_id=tenant_id,
        files=files,
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        parsing_features=parsing_features,
        needs_unification=needs_unification,
        needs_extraction=needs_extraction,
        needs_parsing=needs_parsing,
        needs_validation=needs_validation,
        needs_review=needs_review,
        needs_output_exporting=needs_output_exporting,
    )

    process_document_handler(command_message=command_message)

    process_document.assert_called_with(
        document_id=document_id,
        files=files,
        tenant_id=tenant_id,
        document_type_id=document_type_id,
        needs_unifier=needs_unification,
        needs_extraction=needs_extraction,
        needs_parsing=needs_parsing,
        needs_validation=needs_validation,
        needs_review=needs_review,
        needs_output_exporting=needs_output_exporting,
        language=language,
        engine=engine,
        llm_type=llm_type,
        parsing_features={ParsingFeature(feature) for feature in parsing_features},
        current_status=Status.UNIFICATION,
    )
