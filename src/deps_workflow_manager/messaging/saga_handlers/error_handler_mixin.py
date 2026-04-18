from typing import Union

from deps_workflow_manager.domain.model import Error, ErrorType

from ..commands import CommandWithError
from ..sagas_data import DocumentProcessingSagaData, TypelessDocumentProcessingSagaData

__all__ = ["ErrorHandlerMixin"]

ProcessingSagaData = Union[DocumentProcessingSagaData, TypelessDocumentProcessingSagaData]


class ErrorHandlerMixin:
    @staticmethod
    def evaluate_error_from_reply(data: ProcessingSagaData, reply: CommandWithError) -> None:
        if reply.has_error:
            data.error = ErrorHandlerMixin.build_error_from_reply(reply)

    @staticmethod
    def build_error_from_reply(reply: CommandWithError) -> Error:
        return Error(ErrorType(reply.error_type), reply.error_message)
