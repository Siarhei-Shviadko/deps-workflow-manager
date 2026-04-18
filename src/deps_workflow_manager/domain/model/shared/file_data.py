import os

from ..guards import Guard, ImmutableCheck

__all__ = ["FileData"]


class FileData:
    io = Guard[bytes](bytes, ImmutableCheck())
    path = Guard[str](str, ImmutableCheck())

    def __init__(self, io: bytes, path: str) -> None:
        self.io = io
        self.path = path

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FileData) and self.path == other.path and self.io == other.io

    @property
    def extension(self) -> str:
        return os.path.splitext(self.path)[1]

    @property
    def name(self):
        return os.path.splitext(os.path.basename(self.path))[0]
