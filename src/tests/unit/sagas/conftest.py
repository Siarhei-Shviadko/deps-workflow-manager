from uuid import uuid4

import pytest
from deps_message_flow.sagas.orchestration import SagaInstance, SerializedSagaData


@pytest.fixture
def saga_instance():
    return SagaInstance(
        saga_type="",
        saga_id=str(uuid4()),
        state_name="",
        last_request_id="",
        serialized_saga_data=SerializedSagaData(saga_data_json="", saga_data_type=""),
    )
