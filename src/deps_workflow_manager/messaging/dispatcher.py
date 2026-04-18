from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_workflow_manager.constants import (
    COMMANDS_CHANNEL,
    COMMANDS_QUEUE,
    COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_TYPE_EXCHANGER,
    EXTRACTION_EXCHANGER,
    QUEUE,
    SERVICE_CHANNEL,
)
from deps_workflow_manager.messaging.commands import (
    GetDocumentTypesReply,
    ImportDocument,
    ProcessDocument,
    ProcessDocuments,
    StartAttachmentsProcessing,
    StartDocumentProcessing,
)
from deps_workflow_manager.messaging.events import (
    DocumentTypeCreated,
    DocumentTypeDeleted,
    DocumentTypeUpdated,
    ExtractorAttached,
)

__all__ = ["make_message_dispatcher"]


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_workflow_manager.messaging.handlers import (  # noqa: WPS433
        document_type_created_handler,
        document_type_deleted_handler,
        document_type_extractor_attached_handler,
        document_type_updated_handler,
        get_document_types_reply_handler,
        import_document_handler,
        process_document_handler,
        process_documents_handler,
        start_attachments_processing_handler,
        start_document_processing_handler,
    )

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_REPLIES_CHANNEL)
        .on_message(GetDocumentTypesReply, get_document_types_reply_handler)
        .and_from_channel(COMMANDS_CHANNEL)
        .on_message(ProcessDocuments, process_documents_handler)
        .on_message(ProcessDocument, process_document_handler)
        .on_message(ImportDocument, import_document_handler)
        .and_from_channel(SERVICE_CHANNEL)
        .on_message(StartDocumentProcessing, start_document_processing_handler)
        .on_message(StartAttachmentsProcessing, start_attachments_processing_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    events_handlers = (
        DomainEventHandlersBuilder.for_aggregate_type(DOCUMENT_TYPE_EXCHANGER)
        .on_event(DocumentTypeCreated, document_type_created_handler)
        .on_event(DocumentTypeUpdated, document_type_updated_handler)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .and_for_aggregate_type(EXTRACTION_EXCHANGER)
        .on_event(ExtractorAttached, document_type_extractor_attached_handler)
        .for_queue(QUEUE)
        .build()
    )

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    ded = DomainEventDispatcher(events_handlers, subscriber)
    ded.initialize()

    return subscriber
