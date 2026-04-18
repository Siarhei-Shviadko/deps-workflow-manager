from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_workflow_manager.application import WorkflowStateService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.messaging.saga_state import SagaState

from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

sagas_router = APIRouter(prefix="/sagas", tags=["Sagas"], route_class=MarkerRoute)


__all__ = ["sagas_router"]


@sagas_router.get(
    "/{entity_id}/state",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_model=SagaState,
)
@inject
def get_saga_state(
    entity_id: str,
    workflow_state_service: WorkflowStateService = Depends(Provide[Containers.workflow_state_service]),
):
    return workflow_state_service.get_saga_state(entity_id)
