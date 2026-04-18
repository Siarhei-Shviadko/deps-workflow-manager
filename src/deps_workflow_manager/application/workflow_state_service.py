from deps_message_flow.sagas.orchestration import (
    ISagaInstanceRepository,
    SagaData,
    SagaDataMapping,
    SagaDataSerde,
    SagaInstance,
)

from deps_workflow_manager.domain.exceptions import NotFoundError
from deps_workflow_manager.messaging.saga_state import SagaState

__all__ = ["WorkflowStateService"]


class WorkflowStateService:
    def __init__(
        self,
        saga_instance_repository: ISagaInstanceRepository,
        saga_data_mapping: SagaDataMapping,
    ):
        self._saga_instance_repository = saga_instance_repository
        self._saga_data_mapping = saga_data_mapping

    def get_saga_instance(self, entity_id: str) -> SagaInstance:
        return self._saga_instance_repository.find_for_entity(entity_id=entity_id)

    def get_saga_data(self, entity_id: str) -> SagaData:
        return SagaDataSerde.deserialize_saga_data(
            self.get_saga_instance(entity_id=entity_id).serialized_saga_data,
            self._saga_data_mapping,
        )

    def get_saga_state(self, entity_id: str) -> SagaState:
        try:
            saga = self.get_saga_instance(entity_id)
            return SagaState.from_saga_instance(saga)
        except NotFoundError:
            return SagaState.NONE
