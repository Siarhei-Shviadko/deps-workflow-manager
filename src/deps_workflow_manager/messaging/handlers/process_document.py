import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import NeedsReviewOption, ParsingFeature, Status

from ..commands import ProcessDocument
from ..reply_builder import ReplyBuilder

_logger = logging.getLogger(__name__)

__all__ = ["process_document_handler"]


@inject
def process_document_handler(
    command_message: CommandMessage[ProcessDocument],
    document_processing_service: DocumentProcessingService = Provide[Containers.document_processing_service],
):
    command = command_message.command

    try:
        document_processing_service.process_document(
            tenant_id=command.tenant_id,
            document_id=command.document_id,
            files=command.files,
            document_type_id=command.document_type_id,
            engine=command.engine,
            language=command.language,
            llm_type=command.llm_type,
            parsing_features={ParsingFeature(feature) for feature in command.parsing_features}
            if command.parsing_features
            else None,
            needs_unifier=command.needs_unification,
            needs_extraction=command.needs_extraction,
            needs_parsing=command.needs_parsing,
            needs_validation=command.needs_validation,
            needs_review=NeedsReviewOption(command.needs_review) if command.needs_review else None,
            needs_output_exporting=command.needs_output_exporting,
            current_status=Status.UNIFICATION,
        )

        return [ReplyBuilder.with_success()]

    except Exception as e:
        _logger.error("ProcessDocument failed %s", e, exc_info=True)

        return [ReplyBuilder.with_failure()]
