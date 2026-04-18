from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers

from ..serializers import SerializedDocumentId
from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

__all__ = ["validate_router"]


validate_router = APIRouter(prefix="/validate-workflow", tags=["Validate"], route_class=MarkerRoute)


@validate_router.post(
    "",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def validate(
    document_id: SerializedDocumentId = Body(..., alias="documentId"),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    return workflow_service.validate(document_id.document_id)
