# type: ignore
from fastapi import APIRouter

from .complete_review import complete_router
from .debug import debug_router
from .healthcheck import healthcheck_router
from .plugin_pipeline import plugin_pipeline_router
from .plugin_processing_workflow import process_document_router
from .saga import sagas_router
from .service_info import service_info_router
from .template_pipeline import template_pipeline_router
from .template_processing_workflow import template_process_document_router
from .template_workflow import template_router
from .v2 import document_processing_router, documents_import_router, pipeline_router
from .validate import validate_router
from .workflow_configuration import workflow_configuration_router

__all__ = ["base_router", "v1_router", "v2_router"]

base_router = APIRouter()
base_router.include_router(debug_router)
base_router.include_router(service_info_router)
base_router.include_router(healthcheck_router)

v1_router = APIRouter()
v1_router.include_router(process_document_router)
v1_router.include_router(template_process_document_router)
v1_router.include_router(template_router)
v1_router.include_router(plugin_pipeline_router)
v1_router.include_router(template_pipeline_router)
v1_router.include_router(complete_router)
v1_router.include_router(validate_router)
v1_router.include_router(sagas_router)
v1_router.include_router(workflow_configuration_router)

v2_router = APIRouter()
v2_router.include_router(document_processing_router)
v2_router.include_router(documents_import_router)
v2_router.include_router(pipeline_router)
