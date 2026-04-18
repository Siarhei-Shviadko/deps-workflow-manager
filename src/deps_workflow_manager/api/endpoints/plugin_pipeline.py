from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Response

from deps_workflow_manager.application import WorkflowService
from deps_workflow_manager.containers import Containers

from ..serializers import RunPluginPipelineFromStepRequest, RunPluginPipelineRequest
from .endpoint_marker import MarkerRoute
from .endpoint_visibility import Visibility

plugin_pipeline_router = APIRouter(tags=["Plugin pipeline"], route_class=MarkerRoute)


__all__ = ["plugin_pipeline_router"]


@plugin_pipeline_router.post(
    "/run-plugin-pipeline",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def run_plugin_pipeline(
    run_pipeline_request: RunPluginPipelineRequest,
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    workflow_service.run_plugin_pipeline(
        document_ids=run_pipeline_request.document_ids,
        engine=run_pipeline_request.engine,
        language=run_pipeline_request.language,
        llm_type=run_pipeline_request.llm_type,
        invoke_unifier=run_pipeline_request.invoke_unifier,
        invoke_extraction=run_pipeline_request.invoke_extraction,
    )


@plugin_pipeline_router.post(
    "/run-plugin-pipeline-from-step",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def run_plugin_pipeline_from_step(
    run_pipeline_request: RunPluginPipelineFromStepRequest,
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    workflow_service.run_plugin_pipeline_from_step(
        document_ids=run_pipeline_request.document_ids,
        engine=run_pipeline_request.engine,
        language=run_pipeline_request.language,
        llm_type=run_pipeline_request.llm_type,
        step=run_pipeline_request.step,
    )


@plugin_pipeline_router.post(
    "/retry-plugin-pipeline-last-step",
    status_code=HTTPStatus.ACCEPTED,
    response_class=Response,
    openapi_extra={"visibility": Visibility.PUBLIC},
)
@inject
def retry_plugin_pipeline_last_step(
    document_id: str = Body(..., alias="documentId", min_length=1, embed=True),
    workflow_service: WorkflowService = Depends(Provide[Containers.workflow_service]),
):
    workflow_service.retry_plugin_pipeline_last_step(document_ids=[document_id])
