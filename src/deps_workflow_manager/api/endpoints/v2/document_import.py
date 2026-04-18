from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends

from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.constants import ImportSource
from deps_workflow_manager.domain.model import ParsingFeature

from ...auth import get_current_user_tenant
from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

__all__ = ["documents_import_router"]


documents_import_router = APIRouter(prefix="/import-documents", tags=["Documents Import"], route_class=MarkerRoute)


@documents_import_router.post(
    "",
    status_code=HTTPStatus.OK,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def import_documents(
    paths: list[str],
    source: ImportSource = Body(...),
    document_type_id: Optional[str] = Body(default=None, alias="documentType"),
    engine: Optional[str] = Body(default=None),
    language: Optional[str] = Body(default=None),
    llm_type: Optional[str] = Body(default=None, alias="llmType"),
    invoke_unifier: bool = Body(default=True, alias="invokeUnifier"),
    invoke_extraction: bool = Body(default=True, alias="invokeExtraction"),
    assign_to_me: bool = Body(default=False, alias="assignedToMe"),
    parsing_features: Optional[set[ParsingFeature]] = Body(default=None, alias="parsingFeatures"),
    current_tenant: str = Depends(get_current_user_tenant),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    return workflow_service.import_documents(
        paths=paths,
        source=source,
        document_type_id=document_type_id,
        tenant_id=current_tenant,
        engine=engine,
        language=language,
        llm_type=llm_type,
        invoke_unifier=invoke_unifier,
        invoke_extraction=invoke_extraction,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
    )
