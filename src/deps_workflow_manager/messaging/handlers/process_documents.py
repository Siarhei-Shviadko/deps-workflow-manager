import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import ParsingFeature

from ..commands import ProcessDocuments
from ..reply_builder import ReplyBuilder

_logger = logging.getLogger(__name__)

__all__ = ["process_documents_handler"]


@inject
def process_documents_handler(
    command_message: CommandMessage[ProcessDocuments],
    document_processing: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command
    try:
        for document_name, file_name in command.documents:
            document_processing.full_process_document(
                document_name=document_name,
                file_name=file_name,
                tenant_id=command.tenant_id,
                document_type_id=command.document_type_id,
                engine=command.engine,
                language=command.language,
                llm_type=command.llm_type,
                assign_to_me=command.assign_to_me,
                invoke_unifier=command.invoke_unifier,
                invoke_extraction=command.invoke_extraction,
                parsing_features={ParsingFeature(feature) for feature in command.parsing_features}
                if command.parsing_features
                else None,
            )
        return [ReplyBuilder.with_success()]
    except Exception as e:
        _logger.error("ProcessDocuments failed %s", e, exc_info=True)
        return [ReplyBuilder.with_failure()]
