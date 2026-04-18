from typing import Any

__all__ = ["ContainerData"]


class ContainerData:
    def __init__(self, type_: str, metadata: dict[str, Any], attachments: list[dict[str, Any]]) -> None:
        self.type = type_
        self.metadata = metadata
        self.attachments = attachments

    def __repr__(self) -> str:
        return f"ContainerData(type_={self.type}, metadata={self.metadata}, attachments={self.attachments})"
