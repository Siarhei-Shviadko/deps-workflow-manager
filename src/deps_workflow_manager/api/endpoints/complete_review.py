from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers

from ..serializers import SerializedDocumentId
from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

__all__ = ["complete_router"]


complete_router = APIRouter(prefix="/complete-review-workflow", tags=["Complete review"], route_class=MarkerRoute)


@complete_router.post(
    "",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def complete_review(
    document_id: SerializedDocumentId = Body(..., alias="documentId"),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    return workflow_service.complete_review(document_id.document_id)
