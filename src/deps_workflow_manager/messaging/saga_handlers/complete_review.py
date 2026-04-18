from ..commands import PerformValidationReply
from ..sagas_data import CompleteReviewSagaData

__all__ = ["CompleteReviewHandlers"]


class CompleteReviewHandlers:
    @staticmethod
    def save_validation_result(data: CompleteReviewSagaData, reply: PerformValidationReply) -> None:
        data.validation_result = reply.result
        CompleteReviewHandlers.check_validation_result(data)

    @staticmethod
    def check_validation_result(data: CompleteReviewSagaData):
        if not data.validation_result:
            data.next_state = data.validation_failed_next_step
