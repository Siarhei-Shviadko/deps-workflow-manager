import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_workflow_manager.application import WorkflowConfigurationService
from deps_workflow_manager.containers import Containers

_logger = logging.getLogger(__name__)

__all__ = ["document_type_deleted_handler"]


@inject
def document_type_deleted_handler(  # noqa: WPS463
    dee: DomainEventEnvelope,
    workflow_configuration_service: WorkflowConfigurationService = Provide[Containers.workflow_configuration_service],
) -> None:
    workflow_configuration_service.delete_configuration(
        tenant_id=dee.event.tenant,
        document_type_id=dee.event.document_type,
    )

    _logger.info(
        f"Workflow configuration deleted for document type with id = {dee.event.document_type} "
        + f"from tenant with id = {dee.event.tenant}.",
    )
