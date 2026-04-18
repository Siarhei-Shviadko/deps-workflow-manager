from abc import ABC, abstractmethod

from ..model.document import Document

__all__ = ["IDocumentSpecification"]


class IDocumentSpecification(ABC):
    @abstractmethod
    def check(self) -> None:
        pass

    @staticmethod
    @abstractmethod
    def is_satisfied_by(document: Document) -> bool:
        pass
