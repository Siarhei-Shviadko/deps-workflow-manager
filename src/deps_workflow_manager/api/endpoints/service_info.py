from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_workflow_manager.api.serializers import BuildInfoSerializer
from deps_workflow_manager.containers import Core

from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

__all__ = ["service_info_router"]

service_info_router = APIRouter(prefix="/service-info", tags=["Service Info"], route_class=MarkerRoute)


@service_info_router.get(
    "/version",
    response_model=BuildInfoSerializer,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def get_build_info(build_info=Depends(Provide[Core.build_info])):
    return BuildInfoSerializer(**build_info)
