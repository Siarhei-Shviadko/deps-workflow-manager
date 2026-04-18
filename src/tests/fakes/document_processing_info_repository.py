from typing import Any

from deps_workflow_manager.domain.model import IDocumentProcessingInfoRepository
from deps_workflow_manager.domain.model.workflow_configuration.workflow_configuration import (
    DocumentTypeInfo,
)

__all__ = ["FakeDocumentProcessingInfoRepository"]


class FakeDocumentProcessingInfoRepository(IDocumentProcessingInfoRepository):
    def __init__(self, db: dict[tuple[str, str], Any] = None) -> None:
        self.db = db if db is not None else {}

    def find(self, document_id, tenant_id: str) -> DocumentTypeInfo:  # type: ignore
        return self.db[(document_id, tenant_id)]

    def save(self, info: DocumentTypeInfo) -> None:
        self.db[(info.document_id, info.tenant_id)] = info

    def delete(self, document_id: str, tenant_id: str) -> None:
        self.db.pop((document_id, tenant_id))
