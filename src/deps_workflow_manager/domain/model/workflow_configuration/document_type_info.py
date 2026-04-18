from .extraction_type import ExtractionType

__all__ = ["DocumentTypeInfo"]


class DocumentTypeInfo:  # noqa: WPS230
    def __init__(
        self,
        tenant_id: str,
        document_type_id: str,
        extraction_type: ExtractionType | None = None,
        image_transformations: set[str] | None = None,
        llm_type: str | None = None,
        engine: str | None = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.document_type_id = document_type_id
        self.extraction_type = extraction_type or ExtractionType.NON
        self.image_transformations = image_transformations
        self.llm_type = llm_type
        self.engine = engine

    def __str__(self) -> str:
        return (
            f"<DocumentTypeInfo> tenant_id: {self.tenant_id}, "
            f"document_type_id: {self.document_type_id}, "
            f"extraction_type: {self.extraction_type}, "
            f"image_transformations: {self.image_transformations}, "
            f"llm_type: {self.llm_type}, "
            f"engine: {self.engine}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and self.tenant_id == other.tenant_id
            and self.document_type_id == other.document_type_id
            and self.extraction_type == other.extraction_type
            and self.image_transformations == other.image_transformations
            and self.llm_type == other.llm_type
            and self.engine == other.engine
        )
