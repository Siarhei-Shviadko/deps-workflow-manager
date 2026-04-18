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

__all__ = ["template_process_document_router"]

template_process_document_router = APIRouter(
    prefix="/template-processing-workflow",
    tags=["Document processing"],
    route_class=MarkerRoute,
)


@template_process_document_router.post(
    "",
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def process_via_template(
    document_name: str = Body(..., alias="documentName"),
    document_type: str = Body(..., alias="documentType"),
    file: UploadFile = File(...),
    engine: Optional[str] = Body(None),
    language: Optional[str] = Body(None),
    invoke_unifier: bool = Body(default=True, alias="invokeUnifier"),
    invoke_preprocessor: bool = Body(default=True, alias="invokePreprocessor"),
    invoke_extraction: bool = Body(default=True, alias="invokeExtraction"),
    assign_to_me: bool = Body(default=False, alias="assignedToMe"),
    metadata: Optional[Json] = Body(default=None),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    document_id = workflow_service.process_via_template(
        document_name=document_name,
        document_type_id=document_type,
        engine=engine,
        language=language,
        file_name=file.filename,
        file=file.file.read(),
        invoke_unifier=invoke_unifier,
        invoke_preprocessor=invoke_preprocessor,
        invoke_extraction=invoke_extraction,
        assign_to_me=assign_to_me,
        metadata=metadata,
    )

    return UploadDocumentResponse(document_id=document_id, message=f"Document {document_id} successfully added")
