from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, UploadFile
from pydantic import Json

from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers

from ..serializers import UploadDocumentResponse
from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

__all__ = ["process_document_router"]

process_document_router = APIRouter(
    prefix="/plugin-processing-workflow",
    tags=["Document processing"],
    route_class=MarkerRoute,
)


@process_document_router.post(
    "",
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def process_via_plugin(
    document_name: str = Body(None, alias="documentName"),
    document_type: str = Body(None, alias="documentType"),
    engine: str = Body(None),
    language: str = Body(None),
    llm_type: Optional[str] = Body(default=None, alias="llmType"),
    file: UploadFile = File(...),
    invoke_unifier: Optional[bool] = Body(default=True, alias="invokeUnifier"),
    invoke_extraction: Optional[bool] = Body(default=True, alias="invokeExtraction"),
    assign_to_me: Optional[bool] = Body(default=False, alias="assignedToMe"),
    metadata: Optional[Json] = Body(default=None),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    document_id = workflow_service.process_via_plugin(
        document_name=document_name,
        document_type_id=document_type,
        engine=engine,
        language=language,
        llm_type=llm_type,
        file_name=file.filename,
        file=file.file.read(),
        invoke_unifier=invoke_unifier,
        invoke_extraction=invoke_extraction,
        assign_to_me=assign_to_me,
        metadata=metadata,
    )

    return UploadDocumentResponse(document_id=document_id, message=f"Document {document_id} successfully added")
