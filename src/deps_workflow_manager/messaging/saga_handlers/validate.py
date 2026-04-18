from ..commands import PerformValidationReply
from ..sagas_data import ValidateSagaData

__all__ = ["ValidateHandlers"]


class ValidateHandlers:
    @classmethod
    def save_validation_result(cls, data: ValidateSagaData, reply: PerformValidationReply) -> None:
        data.validation_result = reply.result
        cls.check_validation_result(data)

    @staticmethod
    def check_validation_result(data: ValidateSagaData):
        if not data.validation_result:
            data.next_state = data.validation_failed_next_step
