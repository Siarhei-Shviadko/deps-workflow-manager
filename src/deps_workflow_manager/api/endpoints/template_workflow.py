from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, UploadFile
from starlette.responses import Response

from deps_workflow_manager.api.auth import get_current_user_tenant
from deps_workflow_manager.api.serializers import (
    CreateTemplateFromRequest,
    CreateTemplateRequest,
    CreateTemplateResponse,
)
from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers

from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

__all__ = ["template_router"]

from deps_workflow_manager.domain.model import FileData

template_router = APIRouter(prefix="/template-workflow", tags=["Template creation"], route_class=MarkerRoute)


@template_router.post(
    "",
    status_code=HTTPStatus.CREATED,
    response_model=CreateTemplateResponse,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_template(
    template_data: CreateTemplateRequest,
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
    current_tenant: str = Depends(get_current_user_tenant),
) -> CreateTemplateResponse:
    template_id = workflow_service.create_template(
        name=template_data.name,
        language=template_data.language,
        engine=template_data.engine,
        group_id=template_data.group_id,
        tenant_id=current_tenant,
        description=template_data.description,
    )
    return CreateTemplateResponse(template_id=template_id)


@template_router.post(
    "/from",
    status_code=HTTPStatus.CREATED,
    response_model=CreateTemplateResponse,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_template_from(
    template_data: CreateTemplateFromRequest,
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
    current_tenant: str = Depends(get_current_user_tenant),
) -> CreateTemplateResponse:
    template_id = workflow_service.create_template_from(
        src_template_id=template_data.src_template_id,
        name=template_data.name,
        language=template_data.language,
        engine=template_data.engine,
        group_id=template_data.group_id,
        tenant_id=current_tenant,
        description=template_data.description,
    )
    return CreateTemplateResponse(template_id=template_id)


@template_router.post(
    "/{template_id}/versions",
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def create_version(
    template_id: str,
    files: list[UploadFile] = File(...),
    name: str = Body(...),
    description: Optional[str] = Body(None, max_length=100),
    markup_automatically: bool = Body(default=False, alias="markupAutomatically"),
    current_tenant: str = Depends(get_current_user_tenant),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
) -> None:
    workflow_service.create_version(
        template_id=template_id,
        tenant_id=current_tenant,
        name=name,
        files=[FileData(path=file.filename, io=file.file.read()) for file in files],
        description=description,
        markup_automatically=markup_automatically,
    )


@template_router.delete(
    "/{template_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def delete_template(
    template_id: str,
    current_tenant: str = Depends(get_current_user_tenant),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
) -> None:
    workflow_service.delete_template(template_id=template_id, tenant_id=current_tenant)
