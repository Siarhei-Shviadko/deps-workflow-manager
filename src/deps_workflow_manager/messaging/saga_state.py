from enum import Enum

from deps_message_flow.sagas.orchestration import SagaInstance

__all__ = ["SagaState"]


class SagaState(str, Enum):
    NONE = "NONE"
    PROCESSING = "PROCESSING"
    FAILURE = "FAILURE"
    COMPENSATION = "COMPENSATION"
    SUCCESS = "SUCCESS"

    @classmethod
    def from_saga_instance(cls, saga_instance: SagaInstance) -> "SagaState":
        if saga_instance.failed:
            return cls.FAILURE
        if saga_instance.end_state:
            if saga_instance.compensating:
                return cls.COMPENSATION
            return cls.SUCCESS
        return cls.PROCESSING
