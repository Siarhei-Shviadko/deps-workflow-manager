from http import HTTPStatus
from typing import Optional

from deps_workflow_manager.constants import TEMPLATE_BASE_API_PREFIX, V1_PREFIX
from deps_workflow_manager.domain.exceptions import (
    DocumentTypeAlreadyExistsException,
    IllegalArgument,
    NotFoundError,
)

from .proxy import GenericRestClient

__all__ = ["TemplateService"]


class TemplateService(GenericRestClient):
    SERVICE_NAME = "TemplateService"
    TEMPLATES_URL = f"{TEMPLATE_BASE_API_PREFIX}{V1_PREFIX}/templates"
    _HTTP_STATUS_EXCEPTION_TYPE_MAPPING = {
        HTTPStatus.NOT_FOUND.value: NotFoundError,
        HTTPStatus.CONFLICT.value: DocumentTypeAlreadyExistsException,
        HTTPStatus.UNPROCESSABLE_ENTITY.value: IllegalArgument,
    }

    def create_template(
        self,
        template_id: str,
        name: str,
        language: str,
        engine: str,
        group_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        data = {
            "templateId": template_id,
            "name": name,
            "language": language,
            "engine": engine,
            "groupId": group_id,
            "description": description,
        }
        self.post(url=self.TEMPLATES_URL, json=data)

    def create_template_from(
        self,
        src_template_id: str,
        name: str,
        language: str,
        engine: str,
        template_id: str,
        group_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> str:
        data = {
            "copyFrom": src_template_id,
            "name": name,
            "language": language,
            "engine": engine,
            "templateId": template_id,
            "groupId": group_id,
            "description": description,
        }
        url = f"{self.TEMPLATES_URL}/from"
        return self.post(url=url, json=data)["templateId"]

    def delete_template(self, template_id: str) -> None:
        url = f"{self.TEMPLATES_URL}/{template_id}"
        self.delete(url=url)
