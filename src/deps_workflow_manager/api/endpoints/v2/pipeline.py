from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Response

from deps_workflow_manager.application import DocumentProcessingService
from deps_workflow_manager.containers import Containers

from ...auth import get_current_user_tenant
from ...serializers import RunPipelineFromStepRequest, SerializedDocumentId
from ..endpoint_marker import MarkerRoute
from ..endpoint_visibility import Visibility

pipeline_router = APIRouter(tags=["Pipeline V2"], route_class=MarkerRoute)


__all__ = ["pipeline_router"]


@pipeline_router.post(
    "/run-pipeline",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def run_pipeline(
    document_id: SerializedDocumentId = Body(..., alias="documentId"),
    tenant_id: str = Depends(get_current_user_tenant),
    document_processing_service: DocumentProcessingService = Depends(Provide[Containers.document_processing_service]),
):
    document_processing_service.run_pipeline(
        document_id=document_id.document_id,
        tenant_id=tenant_id,
    )


@pipeline_router.post(
    "/retry-pipeline-last-step",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def retry_pipeline_last_step(
    document_id: SerializedDocumentId = Body(..., alias="documentId"),
    tenant_id: str = Depends(get_current_user_tenant),
    document_processing_service: DocumentProcessingService = Depends(Provide[Containers.document_processing_service]),
):
    document_processing_service.retry_pipeline_last_step(document_id=document_id.document_id, tenant_id=tenant_id)


@pipeline_router.post(
    "/run-pipeline-from-step",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.INTERNAL},
)
@inject
def run_pipeline_from_step(
    run_pipeline_from_step_request: RunPipelineFromStepRequest,
    tenant_id: str = Depends(get_current_user_tenant),
    document_processing_service: DocumentProcessingService = Depends(Provide[Containers.document_processing_service]),
):
    document_processing_service.run_pipeline_from_step(
        document_ids=run_pipeline_from_step_request.document_ids,
        tenant_id=tenant_id,
        step=run_pipeline_from_step_request.step,
        engine=run_pipeline_from_step_request.engine,
        language=run_pipeline_from_step_request.language,
        llm_type=run_pipeline_from_step_request.llm_type,
        parsing_features=run_pipeline_from_step_request.parsing_features,
    )
