import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import ParsingFeature, Status

from ..commands import StartDocumentProcessing
from ..reply_builder import ReplyBuilder

_logger = logging.getLogger(__name__)

__all__ = ["start_document_processing_handler"]


@inject
def start_document_processing_handler(
    command_message: CommandMessage[StartDocumentProcessing],
    document_processing: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command
    _logger.info("Start document processing for command: %s" % command.__dict__)  # noqa: WPS609
    try:
        document_processing.start_document_processing(
            document_id=command.document_id,
            document_name=command.document_name,
            tenant_id=command.tenant_id,
            document_type_id=command.document_type_id,
            engine=command.engine,
            language=command.language,
            llm_type=command.llm_type,
            assign_to_me=command.assign_to_me,
            parsing_features={ParsingFeature(feature) for feature in command.parsing_features}
            if command.parsing_features
            else None,
            document_metadata=command.document_metadata,
            files=command.files,
            needs_unifier=command.needs_unifier,
            needs_extraction=command.needs_extraction,
            current_status=Status(command.from_step),
        )

    except Exception as e:
        _logger.error("ProcessDocument failed %s", e, exc_info=True)

    return [ReplyBuilder.with_success()]
