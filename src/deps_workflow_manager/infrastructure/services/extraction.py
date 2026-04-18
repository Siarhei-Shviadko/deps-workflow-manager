from http import HTTPStatus
from typing import Optional

from deps_workflow_manager.constants import EXTRACTION_BASE_API_PREFIX, V2_PREFIX
from deps_workflow_manager.domain.exceptions import (
    DocumentTypeAlreadyExistsException,
    IllegalArgument,
)

from .proxy import GenericRestClient

__all__ = ["ExtractionService"]


class ExtractionService(GenericRestClient):
    v2_prefix = f"{EXTRACTION_BASE_API_PREFIX}{V2_PREFIX}"
    _HTTP_STATUS_EXCEPTION_TYPE_MAPPING = {
        HTTPStatus.CONFLICT.value: DocumentTypeAlreadyExistsException,
        HTTPStatus.UNPROCESSABLE_ENTITY.value: IllegalArgument,
    }

    def create_document_type(
        self,
        name: str,
        language: str,
        engine: str,
        extractor_type: str,
        description: Optional[str] = None,
    ) -> str:
        url = f"{self.v2_prefix}/document-types/attach-extractor"
        data = {
            "name": name,
            "extractorType": extractor_type,
            "engine": engine,
            "language": language,
            "description": description,
        }
        document_type_data = self.post(url=url, json=data)

        return document_type_data["documentTypeId"]
