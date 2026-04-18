from enum import Enum

__all__ = ["DocumentState", "PROCESSING_STATES", "FINISHED_STATES"]


class DocumentState(str, Enum):
    NEW = "new"

    PREPROCESSING = "preprocessing"
    IDENTIFICATION = "identification"
    DATA_EXTRACTION = "dataExtraction"
    VALIDATION = "validation"
    IN_REVIEW = "inReview"
    FAILED = "failed"
    COMPLETED = "completed"

    # new states
    UNIFICATION = "unification"
    IMAGE_PREPROCESSING = "imagePreprocessing"
    PARSING = "parsing"
    VERSION_IDENTIFICATION = "versionIdentification"
    POSTPROCESSING = "postprocessing"
    NEEDS_REVIEW = "needsReview"
    EXPORTING = "exporting"
    EXPORTED = "exported"
    EXCEPTIONAL_QUEUE = "exceptionalQueue"
    POSTPONED = "postponed"


PROCESSING_STATES = (
    DocumentState.PREPROCESSING,
    DocumentState.IDENTIFICATION,
    DocumentState.DATA_EXTRACTION,
    DocumentState.IDENTIFICATION,
    DocumentState.UNIFICATION,
    DocumentState.IMAGE_PREPROCESSING,
    DocumentState.VERSION_IDENTIFICATION,
    DocumentState.EXPORTING,
    DocumentState.PARSING,
)

FINISHED_STATES = (
    DocumentState.NEW,
    DocumentState.NEEDS_REVIEW,
    DocumentState.COMPLETED,
)
