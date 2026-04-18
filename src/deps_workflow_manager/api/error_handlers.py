import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from deps_workflow_manager.api.serializers.error import ErrorSerializer
from deps_workflow_manager.domain.exceptions import (
    DocumentTypeAlreadyExistsException,
    IllegalArgument,
    NotFoundError,
    WorkflowManagerException,
)
from deps_workflow_manager.messaging.exceptions import MessagingError

logger = logging.getLogger(__name__)


def json_workflow_manager_error_handler(error: WorkflowManagerException, status_code: int):
    error_message = ErrorSerializer(code=error.code, message=str(error)).model_dump()
    return JSONResponse(status_code=status_code, content=error_message)


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(WorkflowManagerException)
    def handle_workflow_manager_exception(req: Request, error: WorkflowManagerException):  # noqa: WPS430
        mapper = [
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (DocumentTypeAlreadyExistsException, HTTPStatus.CONFLICT),
            (IllegalArgument, HTTPStatus.UNPROCESSABLE_ENTITY),
            (WorkflowManagerException, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_workflow_manager_error_handler(error, status_code)

    @app.exception_handler(MessagingError)
    def messaging_error(req: Request, exc: MessagingError):  # noqa: WPS430
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=ErrorSerializer(code=exc.code, message=str(exc)).model_dump(),
        )

    @app.exception_handler(ValidationError)
    def bad_request(req: Request, exc: ValidationError):  # noqa: WPS430
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorSerializer(code="bad_request", message=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):  # noqa: WPS430
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorSerializer(code="unhandled_error", message=str(error)).model_dump(),
        )
