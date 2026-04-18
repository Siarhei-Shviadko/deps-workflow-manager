import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import CommandReplyOutcome, ReplyMessageHeaders
from deps_message_flow.commands.consumer.command_message import CommandMessage

from deps_workflow_manager.application import WorkflowConfigurationService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import DocumentTypeInfo, ExtractionType

_logger = logging.getLogger(__name__)

__all__ = ["get_document_types_reply_handler"]


def is_command_successful(command_message: CommandMessage) -> bool:
    return (
        command_message.message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME)
        == CommandReplyOutcome.SUCCESS.name
    )


@inject
def get_document_types_reply_handler(  # noqa: WPS463
    command_message: CommandMessage,
    workflow_configuration_service: WorkflowConfigurationService = Provide[Containers.workflow_configuration_service],
) -> None:
    if is_command_successful(command_message):
        document_types = command_message.command.document_types
        workflow_configuration_service.save_configuration_for(
            document_types=[
                DocumentTypeInfo(
                    tenant_id=document_type["tenant_id"],
                    document_type_id=document_type["document_type_id"],
                    extraction_type=ExtractionType(document_type.get("extraction_type"))
                    if document_type.get("extraction_type")
                    else ExtractionType.NON,
                    image_transformations=set(document_type.get("image_transformations"))
                    if document_type.get("image_transformations")
                    else None,
                    llm_type=document_type.get("llm_type"),
                    engine=document_type.get("engine"),
                )
                for document_type in document_types
            ],
        )

        _logger.info("Workflow configuration updated successfully")

    else:
        _logger.error(f"Failed to get document types. Command headers: {command_message.message.headers}")
