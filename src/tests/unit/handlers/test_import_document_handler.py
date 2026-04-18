from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.messaging.handlers import import_document_handler


def test_import_document_handler__document_sent_to_preprocessing(import_document_command_message, this_user, mocker):
    process_document = mocker.patch.object(DocumentProcessingService, "process_document")

    import_document_handler(import_document_command_message)

    process_document.assert_called_with(
        document_name=import_document_command_message.command.document_name,
        files=[import_document_command_message.command.file_path],
        tenant_id=this_user["organisation"],
        document_type_id=import_document_command_message.command.document_type,
        document_metadata=import_document_command_message.command.document_metadata,
        needs_unifier=import_document_command_message.command.invoke_unifier,
        needs_extraction=import_document_command_message.command.invoke_extraction,
        parsing_features=import_document_command_message.command.parsing_features,
        language=import_document_command_message.command.language,
        engine=import_document_command_message.command.engine,
        llm_type=import_document_command_message.command.llm_type,
    )
