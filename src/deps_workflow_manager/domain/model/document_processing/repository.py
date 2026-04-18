from typing import Protocol

from .document_processing import DocumentProcessingInfo

__all__ = ["IDocumentProcessingInfoRepository"]


class IDocumentProcessingInfoRepository(Protocol):
    def find(self, document_id: str, tenant_id: str) -> DocumentProcessingInfo:
        pass

    def save(self, info: DocumentProcessingInfo) -> None:
        pass

    def delete(self, document_id: str, tenant_id: str) -> None:
        pass
