from typing import Any

from deps_workflow_manager.domain.model import DocumentTypeInfo

__all__ = ["DocumentTypeInfoMapper"]


class DocumentTypeInfoMapper:
    @staticmethod
    def to_dict(document_type_info: DocumentTypeInfo) -> dict[str, Any]:
        return {
            "tenant_id": document_type_info.tenant_id,
            "document_type_id": document_type_info.document_type_id,
            "extraction_type": document_type_info.extraction_type.value,
            "image_transformations": list(document_type_info.image_transformations)
            if document_type_info.image_transformations
            else None,
            "llm_type": document_type_info.llm_type,
            "engine": document_type_info.engine,
        }
