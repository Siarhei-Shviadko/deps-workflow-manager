import enum

__all__ = ["Status"]


class Status(enum.Enum):
    NEW = "new"
    UNIFICATION = "unification"
    CLASSIFICATION = "classification"
    VERSION_CLASSIFICATION = "version_classification"
    IMAGE_PREPROCESSING = "image_preprocessing"
    PARSING = "parsing"
    EXTRACTION = "extraction"
    POSTPROCESSING = "postprocessing"
    VALIDATION = "validation"
    NEEDS_REVIEW = "needs_review"
    EXPORTING = "exporting"
    EXPORTED = "exported"

    FAILURE = "failure"
    EXCEPTIONAL_QUEUE = "exceptional_queue"
    POSTPONED = "postponed"

    COMPLETED = "completed"
