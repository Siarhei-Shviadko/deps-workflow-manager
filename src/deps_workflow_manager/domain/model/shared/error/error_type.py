import enum

__all__ = ["ErrorType"]


class ErrorType(enum.Enum):
    SYSTEM = "system"
    BUSINESS = "business"
    VALIDATION = "validation"
