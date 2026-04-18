import pytest
from deps_message_flow.sagas.orchestration import SagaInstance

from deps_workflow_manager.messaging.saga_state import SagaState


@pytest.mark.saga_state
def test_saga_in_progress(saga_instance: SagaInstance):
    assert SagaState.from_saga_instance(saga_instance) == SagaState.PROCESSING


@pytest.mark.saga_state
def test_saga_failed(saga_instance: SagaInstance):
    saga_instance.failed = True
    assert SagaState.from_saga_instance(saga_instance) == SagaState.FAILURE


@pytest.mark.saga_state
def test_saga_compensating(saga_instance: SagaInstance):
    saga_instance.end_state = True
    saga_instance.compensating = True
    assert SagaState.from_saga_instance(saga_instance) == SagaState.COMPENSATION


@pytest.mark.saga_state
def test_saga_success(saga_instance: SagaInstance):
    saga_instance.end_state = True
    assert SagaState.from_saga_instance(saga_instance) == SagaState.SUCCESS
