import pytest

from deps_workflow_manager.domain.exceptions import NotFoundError
from deps_workflow_manager.messaging.saga_state import SagaState


def test_workflow_sate_service__get_saga_instance__not_found(workflow_state_service):
    with pytest.raises(NotFoundError):
        workflow_state_service.get_saga_instance("qwerty")


def test_workflow_sate_service__get_saga_data__not_found(workflow_state_service):
    with pytest.raises(NotFoundError):
        workflow_state_service.get_saga_data("qwerty")


def test_workflow_sate_service__get_saga_instance__success(
    workflow_state_service,
    saga_instance_repo,
    saga_instance,
    entity_id,
):
    assert saga_instance_repo.save(saga_instance) == workflow_state_service.get_saga_instance(entity_id)


def test_workflow_sate_service__get_saga_data__success(
    workflow_state_service,
    saga_instance_repo,
    saga_instance,
    entity_id,
):
    saga_instance_repo.save(saga_instance)
    saga_data = workflow_state_service.get_saga_data(entity_id)

    assert saga_data.entity_id == entity_id


def test_workflow_sate_service__get_saga_state__processing(
    workflow_state_service,
    saga_instance_repo,
    saga_instance,
    entity_id,
):
    saga_instance_repo.save(saga_instance)

    assert workflow_state_service.get_saga_state(entity_id) == SagaState.PROCESSING


def test_workflow_sate_service__get_saga_state__none(
    workflow_state_service,
    saga_instance_repo,
    saga_instance,
    entity_id,
):
    assert workflow_state_service.get_saga_state(entity_id) == SagaState.NONE
