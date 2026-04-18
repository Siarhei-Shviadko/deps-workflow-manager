from typing import Any, Protocol, Type, TypeVar

from ...exceptions import IllegalArgument
from .attribute_name import AttributeName

T = TypeVar("T", contravariant=True)
MAX_LENGTH = 150


class Check(Protocol[T]):
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        ...  # noqa: WPS428


class NoneCheck:
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if value is None:
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object should be provided.",
            )


class TypeCheck:
    def __init__(self, type_: Type[T]) -> None:
        self._type = type_

    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if not isinstance(value, self._type):
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object "
                f"should be {self._type.__name__}.",  # noqa: WPS326
            )


class ImmutableCheck:
    def is_correct(self, domain_obj: Any, value: T, attribute_name: AttributeName) -> None:
        if hasattr(domain_obj, attribute_name.private) and getattr(domain_obj, attribute_name.private) is not None:
            raise IllegalArgument(
                f"Attribute {attribute_name.public} for {domain_obj.__class__.__name__} object cannot be changed.",
            )
