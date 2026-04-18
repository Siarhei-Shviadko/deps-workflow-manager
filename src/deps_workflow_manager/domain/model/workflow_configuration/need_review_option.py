from enum import Enum

__all__ = ["NeedsReviewOption"]


class NeedsReviewOption(str, Enum):
    ALWAYS_REVIEW = "always_review"
    REVIEW_IF_VALIDATION_FAILURE = "review_if_validation_failure"
    NO_REVIEW = "no_review"

    @property
    def needs_user_verification(self) -> bool:
        return self == NeedsReviewOption.ALWAYS_REVIEW

    @property
    def needs_review_on_validation_failure(self) -> bool:
        return self == NeedsReviewOption.REVIEW_IF_VALIDATION_FAILURE

    @classmethod
    def from_flags(cls, needs_user_verification: bool, needs_review_on_validation_failure: bool) -> "NeedsReviewOption":
        if needs_user_verification:
            return cls.ALWAYS_REVIEW
        if needs_review_on_validation_failure:
            return cls.REVIEW_IF_VALIDATION_FAILURE
        return cls.NO_REVIEW
