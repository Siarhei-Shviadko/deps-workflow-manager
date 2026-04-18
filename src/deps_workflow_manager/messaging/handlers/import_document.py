import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage

from deps_workflow_manager.api.auth import get_current_user_tenant
from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import ParsingFeature

from ..commands import ImportDocument
from ..reply_builder import ReplyBuilder

_logger = logging.getLogger(__name__)

__all__ = ["import_document_handler"]


@inject
def import_document_handler(
    command_message: CommandMessage[ImportDocument],
    document_processing: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command
    try:
        document_processing.process_document(
            document_name=command.document_name,
            files=[command.file_path],
            tenant_id=get_current_user_tenant(),
            document_type_id=command.document_type,
            document_metadata=command.document_metadata,
            needs_unifier=command.invoke_unifier,
            needs_extraction=command.invoke_extraction,
            parsing_features={ParsingFeature(feature) for feature in command.parsing_features}
            if command.parsing_features
            else None,
            engine=command.engine,
            language=command.language,
            llm_type=command.llm_type,
        )
        _logger.info("Imported document was sent to preprocessing")
        return [ReplyBuilder.with_success()]
    except Exception as e:
        _logger.error("Failed to send imported document to preprocessing: %s", e)
        return [ReplyBuilder.with_failure()]
