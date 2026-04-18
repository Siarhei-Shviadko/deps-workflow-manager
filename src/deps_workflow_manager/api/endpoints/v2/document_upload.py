from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, Response, UploadFile
from fastapi.exceptions import HTTPException
from pydantic import Json, ValidationError

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.containers import Containers
from deps_workflow_manager.domain.model import ParsingFeature

from ...auth import get_current_user_tenant
from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

__all__ = ["document_processing_router"]

document_processing_router = APIRouter(
    tags=["Document processing"],
    route_class=MarkerRoute,
)


def get_parsing_features(
    parsing_features: Json = Body([], alias="parsingFeatures"),
) -> Optional[set[ParsingFeature]]:
    try:
        return {ParsingFeature(feature) for feature in parsing_features} if parsing_features else None
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=e.errors())


@document_processing_router.post(
    "/upload-document",
    status_code=HTTPStatus.CREATED,
    openapi_extra={"visibility": Visibility.INTERNAL},
    response_class=Response,
)
@inject
def upload_document(
    document_name: str = Body(..., alias="documentName"),
    file: UploadFile = File(...),
    document_type_id: Optional[str] = Body(default=None, alias="documentType"),
    engine: Optional[str] = Body(default=None),
    language: Optional[str] = Body(default=None),
    llm_type: Optional[str] = Body(default=None, alias="llmType"),
    parsing_features: Optional[set[ParsingFeature]] = Depends(get_parsing_features),
    output_profile_ids: Optional[list[str]] = Body(default=None, alias="outputProfileIds"),
    needs_unifier: bool = Body(default=True, alias="needsUnifier"),
    needs_extraction: bool = Body(default=True, alias="needsExtraction"),
    assign_to_me: bool = Body(default=False, alias="assignedToMe"),
    metadata: Optional[Json] = Body(default=None),
    tenant_id: str = Depends(get_current_user_tenant),
    document_processing_service: DocumentProcessingService = Depends(Provide[Containers.document_processing_service]),
):
    document_processing_service.process_document(
        tenant_id=tenant_id,
        document_name=document_name,
        file_name=file.filename,
        file=file.file.read(),
        document_type_id=document_type_id,
        engine=engine,
        language=language,
        llm_type=llm_type,
        assign_to_me=assign_to_me,
        parsing_features=parsing_features,
        output_profile_ids=output_profile_ids,
        needs_unifier=needs_unifier,
        needs_extraction=needs_extraction,
        document_metadata=metadata,
    )

    return Response(status_code=HTTPStatus.CREATED)
