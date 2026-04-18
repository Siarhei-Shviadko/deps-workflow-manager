import logging

from dependency_injector.wiring import Provide, inject
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_workflow_manager.api import get_current_user_tenant
from deps_workflow_manager.application import WorkflowConfigurationService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import DocumentTypeInfo, ExtractionType

_logger = logging.getLogger(__name__)

__all__ = ["document_type_extractor_attached_handler"]


@inject
def document_type_extractor_attached_handler(  # noqa: WPS463
    dee: DomainEventEnvelope,
    workflow_configuration_service: WorkflowConfigurationService = Provide[Containers.workflow_configuration_service],
) -> None:
    tenant_id = get_current_user_tenant()
    workflow_configuration_service.save_configuration_for(
        document_types=[
            DocumentTypeInfo(
                tenant_id=tenant_id,
                document_type_id=dee.event.document_type_id,
                extraction_type=ExtractionType(dee.event.extraction_type),
                image_transformations=set(dee.event.image_transformations) if dee.event.image_transformations else None,
                engine=dee.event.engine,
            ),
        ],
    )

    _logger.info(
        f"Workflow configuration updated for document type with id = {dee.event.document_type_id} "
        + f"from tenant with id = {tenant_id}.",
    )
