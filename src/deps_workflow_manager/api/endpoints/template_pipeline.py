from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Response

from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers

from ..serializers import RunTemplatePipelineFromStepRequest, RunTemplatePipelineRequest
from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

template_pipeline_router = APIRouter(tags=["Template pipeline"], route_class=MarkerRoute)


__all__ = ["template_pipeline_router"]


@template_pipeline_router.post(
    "/run-template-pipeline",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def run_template_pipeline(
    run_pipeline_request: RunTemplatePipelineRequest,
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    workflow_service.run_template_pipeline(
        document_ids=run_pipeline_request.document_ids,
        engine=run_pipeline_request.engine,
        language=run_pipeline_request.language,
        invoke_unifier=run_pipeline_request.invoke_unifier,
        invoke_preprocessor=run_pipeline_request.invoke_preprocessor,
        invoke_extraction=run_pipeline_request.invoke_extraction,
    )


@template_pipeline_router.post(
    "/run-template-pipeline-from-step",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def run_template_pipeline_from_step(
    run_pipeline_request: RunTemplatePipelineFromStepRequest,
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    workflow_service.run_template_pipeline_from_step(
        document_ids=run_pipeline_request.document_ids,
        engine=run_pipeline_request.engine,
        language=run_pipeline_request.language,
        step=run_pipeline_request.step,
    )


@template_pipeline_router.post(
    "/retry-template-pipeline-last-step",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def retry_template_pipeline_last_step(
    document_id: str = Body(..., alias="documentId", min_length=1, embed=True),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    workflow_service.retry_template_pipeline_last_step(document_ids=[document_id])
