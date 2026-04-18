import json
from http import HTTPStatus
from typing import Any, Optional

from deps_workflow_manager.constants import DOCUMENT_BASE_API_PREFIX, V1_PREFIX
from deps_workflow_manager.domain.exceptions import NotFoundError
from deps_workflow_manager.domain.model import Document

from .proxy import GenericRestClient
from .serializers import GetBriefDocumentsInfoResponse

__all__ = ["DocumentService"]


class DocumentService(GenericRestClient):
    DOCUMENTS_URL = f"{DOCUMENT_BASE_API_PREFIX}{V1_PREFIX}"
    _HTTP_STATUS_EXCEPTION_TYPE_MAPPING = {
        HTTPStatus.NOT_FOUND: NotFoundError,
    }

    def get_brief_documents_info(self, ids: list[str]) -> list[Document]:
        query = "&".join([f"documentIds={id_}" for id_ in ids])
        url = f"{self.DOCUMENTS_URL}/brief-documents-info?{query}"
        document_data = self.get(url=url)

        return [document.to_model() for document in GetBriefDocumentsInfoResponse(**document_data).documents]

    def get_full_document_info(self, id_: str) -> dict[str, Any]:
        url = f"{self.DOCUMENTS_URL}/documents/{id_}"
        return self.get(url=url)

    def update_document_detail(self, id_: str, data: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.DOCUMENTS_URL}/documents/{id_}"
        return self.patch(url=url, json=data)

    def document_type_has_docs(self, doc_type_code: str) -> bool:
        query = "&".join((f'types=["{doc_type_code}"]', "sortDirect=desc", "page=1", "perPage=1"))
        url = f"{self.DOCUMENTS_URL}/documents?{query}"
        response = self.get(url=url)
        return response["meta"]["total"] > 0

    def create_document(
        self,
        document_name: str,
        files: list[str],
        document_type_id: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        assign_to_me: bool = False,
        metadata: dict[str, Any] = None,
    ) -> str:
        payload = {
            "documentName": document_name,
            "files": files,
            "documentTypeId": document_type_id,
            "engine": engine,
            "language": language,
            "assignToMe": assign_to_me,
            "metadata": json.dumps(metadata) if metadata else None,
        }

        url = f"{self.DOCUMENTS_URL}/documents/create-document"

        response = self.post(url=url, json=payload)

        return response["documentId"]
