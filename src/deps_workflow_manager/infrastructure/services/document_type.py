from deps_workflow_manager.constants import DOCUMENT_TYPE_BASE_API_PREFIX, V1_PREFIX

from .proxy import GenericRestClient

__all__ = ["DocumentTypeService"]


class DocumentTypeService(GenericRestClient):
    TYPES_URL = f"{DOCUMENT_TYPE_BASE_API_PREFIX}{V1_PREFIX}/types"

    def delete_document_type(self, document_type_id: str) -> None:
        self.delete(url=f"{self.TYPES_URL}/{document_type_id}")
