import json

import pytest
from deps_message_flow.sagas.orchestration import SerializedSagaData

from deps_workflow_manager.domain.exceptions import NotFoundError


def test_saga_repository__find__failure(saga_instance_repo):
    with pytest.raises(NotFoundError):
        saga_instance_repo.find("qwerty")


def test_saga_repository__find_for_entity__failure(saga_instance_repo):
    with pytest.raises(NotFoundError):
        saga_instance_repo.find_for_entity("qwerty")


def test_saga_repository__save__update__find__success(saga_instance_repo, saga_instance, entity_id):
    saved_saga_instance = saga_instance_repo.save(saga_instance)
    found_saga_instance = saga_instance_repo.find_for_entity(entity_id)

    assert found_saga_instance == saved_saga_instance

    new_entity_id = "test"
    saved_saga_instance.saga_type = "NewSagaType"
    saved_saga_instance.state_name = "NewState"
    saved_saga_instance.last_request_id = "NewLastRequestId"
    saved_saga_instance.serialized_saga_data = SerializedSagaData(
        saga_data_type="NewData",
        saga_data_json=json.dumps({"entity_id": new_entity_id}),
    )
    saved_saga_instance.end_state = True
    saved_saga_instance.compensating = True
    saved_saga_instance.failed = True

    updated_saga_instance = saga_instance_repo.update(saved_saga_instance)
    found_saga_instance = saga_instance_repo.find(updated_saga_instance.saga_id)

    assert found_saga_instance == saga_instance_repo.find_for_entity(new_entity_id)
    assert saved_saga_instance.saga_type == found_saga_instance.saga_type
    assert saved_saga_instance.state_name == found_saga_instance.state_name
    assert saved_saga_instance.last_request_id == found_saga_instance.last_request_id
    assert saved_saga_instance.serialized_saga_data == found_saga_instance.serialized_saga_data
    assert saved_saga_instance.end_state == found_saga_instance.end_state
    assert saved_saga_instance.compensating == found_saga_instance.compensating
    assert saved_saga_instance.failed == found_saga_instance.failed


def test_saga_repository__save_multiple_sagas_for_one_entity__success(saga_instance_repo, saga_instance, entity_id):
    first_saga_instance = saga_instance_repo.save(saga_instance)

    assert first_saga_instance == saga_instance_repo.find_for_entity(entity_id)

    second_saga_instance = saga_instance_repo.save(saga_instance)

    assert second_saga_instance == saga_instance_repo.find_for_entity(entity_id)
