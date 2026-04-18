import json
import logging
from http import HTTPStatus
from typing import Any

from fastapi import Request

from deps_workflow_manager.domain.exceptions import AuthError
from deps_workflow_manager.infrastructure.context_vars import user

__all__ = ["set_user_from_token", "get_current_user_tenant"]

_logger = logging.getLogger(__name__)

PUBLIC_ENDPOINTS = (
    "/api/workflow-manager/v1/docs",
    "/api/workflow-manager/v1/openapi.json",
    "/api/workflow-manager/debug/500",
    "/api/workflow-manager/healthcheck",
    "/api/workflow-manager/service-info/version",
    "/favicon.ico",
)


def set_user_from_token(
    request: Request,
) -> None:
    if request.url.path in PUBLIC_ENDPOINTS:
        return None

    try:
        user_info = json.loads(request.headers["deps-token"])
        _validate_deps_token(user_info)
        user_info["deps_token"] = request.headers["deps-token"]
        user.set(user_info)

    except KeyError:
        raise AuthError("Deps-token doesn't provided.")
    except TypeError:
        raise AuthError("Provided deps-token isn't correct.")


def _validate_deps_token(deps_token: dict[str, Any]) -> None:
    if not deps_token:
        raise AuthError("Deps-token validation fails. Deps-token is invalid.")
    elif not deps_token.get("organisation"):
        raise AuthError(
            detail="User without organisation.",
            status_code=HTTPStatus.FORBIDDEN,
        )


def get_current_user_tenant() -> str:
    current_user = user.get()

    return current_user["organisation"]
