from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path

from deps_workflow_manager.application import WorkflowConfigurationService
from deps_workflow_manager.containers import Containers

from ..auth import get_current_user_tenant
from ..serializers import (
    UpdateWorkflowConfigurationRequest,
    WorkflowConfigurationResponse,
)
from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

__all__ = ["workflow_configuration_router"]


workflow_configuration_router = APIRouter(
    prefix="/workflow-configuration",
    tags=["Workflow configuration"],
    route_class=MarkerRoute,
)


@workflow_configuration_router.patch(
    "",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def update_workflow_configuration(
    update_workflow_configuration_request: UpdateWorkflowConfigurationRequest,
    current_tenant: str = Depends(get_current_user_tenant),
    workflow_configuration: WorkflowConfigurationService = Depends(Provide[Containers.workflow_configuration_service]),
):
    return workflow_configuration.update_configuration(
        tenant_id=current_tenant,
        document_type_id=update_workflow_configuration_request.document_type_id,
        engine=update_workflow_configuration_request.engine,
        parsing_features=update_workflow_configuration_request.parsing_features,
        needs_extraction=update_workflow_configuration_request.needs_extraction,
        needs_postprocessing=update_workflow_configuration_request.needs_postprocessing,
        needs_validation=update_workflow_configuration_request.needs_validation,
        needs_review=update_workflow_configuration_request.needs_review,
        needs_output_exporting=update_workflow_configuration_request.needs_output_exporting,
    )


@workflow_configuration_router.get(
    "/{documentTypeId}",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=WorkflowConfigurationResponse,
)
@inject
def get_workflow_configuration(
    document_type_id: str = Path(..., alias="documentTypeId"),
    current_tenant: str = Depends(get_current_user_tenant),
    workflow_configuration: WorkflowConfigurationService = Depends(Provide[Containers.workflow_configuration_service]),
):
    configuration = workflow_configuration.get_configuration(
        document_type_id=document_type_id,
        tenant_id=current_tenant,
    )
    return WorkflowConfigurationResponse.from_domain(configuration)


@workflow_configuration_router.get(
    "",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=dict[str, WorkflowConfigurationResponse],
)
@inject
def get_workflow_configurations(
    current_tenant: str = Depends(get_current_user_tenant),
    workflow_configuration: WorkflowConfigurationService = Depends(Provide[Containers.workflow_configuration_service]),
):
    configurations = workflow_configuration.find_all_configurations(tenant_id=current_tenant)
    return {
        configuration.document_type_id: WorkflowConfigurationResponse.from_domain(configuration)
        for configuration in configurations
    }
