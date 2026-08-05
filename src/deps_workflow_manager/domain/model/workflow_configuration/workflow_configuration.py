from ..shared import ParsingFeature
from .document_type_info import DocumentTypeInfo
from .extraction_type import ExtractionType
from .need_review_option import NeedsReviewOption

__all__ = ["WorkflowConfiguration"]


class WorkflowConfiguration:  # noqa: WPS230
    def __init__(
        self,
        tenant_id: str,
        document_type_id: str,
        extraction_type: ExtractionType | None = None,
        image_transformations: set[str] | None = None,
        llm_type: str | None = None,
        parsing_features: set[ParsingFeature] | None = None,
        needs_extraction: bool = True,
        needs_postprocessing: bool = False,
        needs_validation: bool = False,
        needs_user_verification: bool = False,
        needs_output_exporting: bool = False,
        needs_review_on_validation_failure: bool = False,
        engine: str | None = None,
    ) -> None:
        self.document_type_info = DocumentTypeInfo(
            tenant_id=tenant_id,
            document_type_id=document_type_id,
            extraction_type=extraction_type,
            image_transformations=image_transformations,
            llm_type=llm_type,
            engine=engine,
        )
        self.parsing_features = parsing_features if parsing_features is not None else {ParsingFeature.TEXT}
        self.needs_extraction = needs_extraction
        self.needs_postprocessing = needs_postprocessing
        self.needs_validation = needs_validation
        self.needs_user_verification = needs_user_verification
        self.needs_output_exporting = needs_output_exporting
        self.needs_review_on_validation_failure = needs_review_on_validation_failure

    def __str__(self) -> str:
        return (
            f"<WorkflowConfiguration> tenant_id: {self.tenant_id}, "
            f"document_type_id: {self.document_type_id}, "
            f"extraction_type: {self.extraction_type}, "
            f"image_transformations: {self.image_transformations}, "
            f"parsing_features: {self.parsing_features}, "
            f"needs_extraction: {self.needs_extraction}, "
            f"needs_postprocessing: {self.needs_postprocessing}, "
            f"needs_validation: {self.needs_validation}, "
            f"needs_user_verification: {self.needs_user_verification}"
            f"needs_output_exporting: {self.needs_output_exporting}"
            f"needs_review_on_validation_failure: {self.needs_review_on_validation_failure}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)  # noqa: WPS222
            and self.document_type_info == other.document_type_info
            and self.parsing_features == other.parsing_features
            and self.needs_extraction == other.needs_extraction
            and self.needs_postprocessing == other.needs_postprocessing
            and self.needs_validation == other.needs_validation
            and self.needs_user_verification == other.needs_user_verification
            and self.needs_output_exporting == other.needs_output_exporting
            and self.needs_review_on_validation_failure == other.needs_review_on_validation_failure
        )

    @property
    def tenant_id(self) -> str:
        return self.document_type_info.tenant_id

    @property
    def document_type_id(self) -> str:
        return self.document_type_info.document_type_id

    @property
    def image_transformations(self) -> set[str] | None:
        return self.document_type_info.image_transformations

    @image_transformations.setter
    def image_transformations(self, value: set[str] | None) -> None:
        self.document_type_info.image_transformations = value

    @property
    def extraction_type(self) -> ExtractionType | None:
        return self.document_type_info.extraction_type

    @extraction_type.setter
    def extraction_type(self, value: ExtractionType | None) -> None:
        self.document_type_info.extraction_type = value

    @property
    def needs_image_preprocessing(self) -> bool:
        return self.extraction_type == ExtractionType.TEMPLATE or bool(self.image_transformations)

    @property
    def llm_type(self) -> str | None:
        return self.document_type_info.llm_type

    @llm_type.setter
    def llm_type(self, value: str) -> None:
        self.document_type_info.llm_type = value

    @property
    def engine(self) -> str | None:
        return self.document_type_info.engine

    @engine.setter
    def engine(self, value: str) -> None:
        self.document_type_info.engine = value

    @property
    def needs_review(self) -> NeedsReviewOption:
        return NeedsReviewOption.from_flags(
            needs_user_verification=self.needs_user_verification,
            needs_review_on_validation_failure=self.needs_review_on_validation_failure,
        )
