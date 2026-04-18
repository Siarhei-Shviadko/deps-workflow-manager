from ..commands import (
    AutoMarkupFailedReply,
    CreateVersionReply,
    PreprocessReferencePageReply,
)
from ..sagas_data import VersionCreationSagaData

__all__ = ["VersionCreationHandlers"]


class VersionCreationHandlers:
    @staticmethod
    def preprocess_reference_pages(data: VersionCreationSagaData, reply: PreprocessReferencePageReply) -> None:
        data.preprocessed_blob_names = reply.blob_names

    @staticmethod
    def create_version(data: VersionCreationSagaData, reply: CreateVersionReply) -> None:
        data.version_id = reply.version_id

    @staticmethod
    def auto_markup_failed(data: VersionCreationSagaData, reply: AutoMarkupFailedReply) -> None:
        data.auto_markup_failed = True
