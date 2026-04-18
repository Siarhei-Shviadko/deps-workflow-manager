from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.exporting_step
@pytest.mark.parametrize(
    "error,exceptional_queue_enabled,expected_status",
    [
        [Error(ErrorType.SYSTEM, uuid4().hex), False, Status.FAILURE],
        [Error(ErrorType.BUSINESS, uuid4().hex), False, Status.POSTPONED],
        [Error(ErrorType.BUSINESS, uuid4().hex), True, Status.EXCEPTIONAL_QUEUE],
        [None, False, Status.EXPORTED],
    ],
)
def test_exporting(
    error,
    exceptional_queue_enabled,
    expected_status,
):
    s = StepFactory(error=error, exceptional_queue_enabled=exceptional_queue_enabled).make_exporting_step()

    ns = s.next_step()

    assert expected_status == ns.status
