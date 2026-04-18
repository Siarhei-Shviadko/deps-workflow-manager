from typing import Any, Mapping

from deps_workflow_manager.domain.model import DocumentProcessingInfo, ParsingFeature

__all__ = ["DocumentProcessingInfoMapper"]


class DocumentProcessingInfoMapper:
    @staticmethod
    def from_dict(raw_info: Mapping[str, Any]) -> DocumentProcessingInfo:
        return DocumentProcessingInfo(
            document_id=raw_info["document_id"],
            tenant_id=raw_info["tenant_id"],
            needs_unifier=raw_info["needs_unifier"],
            needs_extraction=raw_info["needs_extraction"],
            parsing_features={ParsingFeature(feature) for feature in raw_info["parsing_features"]}
            if raw_info["parsing_features"]
            else None,
            assign_to_me=raw_info["assign_to_me"],
        )

    @staticmethod
    def to_dict(info: DocumentProcessingInfo) -> dict[str, Any]:
        return {
            "document_id": info.document_id,
            "tenant_id": info.tenant_id,
            "needs_unifier": info.needs_unifier,
            "needs_extraction": info.needs_extraction,
            "parsing_features": list(info.parsing_features) if info.parsing_features else None,
            "assign_to_me": info.assign_to_me,
        }
