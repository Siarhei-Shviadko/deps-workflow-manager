import pytest

from deps_workflow_manager.domain.model import Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    PipelineStateMachine,
)


@pytest.mark.state_machine
def test_pipeline_state_machine():
    state_machine = PipelineStateMachine(current_status=Status.NEW, needs_unification=True)

    assert state_machine.current_step.status == Status.NEW

    assert state_machine.next_step.status == Status.UNIFICATION
