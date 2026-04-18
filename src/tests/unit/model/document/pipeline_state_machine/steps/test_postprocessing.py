from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.postprocessing_step
@pytest.mark.parametrize(
    (
        "error,"
        "needs_validation,"
        "needs_user_verification,"
        "needs_output_exporting,"
        "exceptional_queue_enabled,"
        "expected_status"
    ),
    [
        [Error(ErrorType.SYSTEM, uuid4().hex), False, False, False, False, Status.COMPLETED],
        [Error(ErrorType.BUSINESS, uuid4().hex), False, False, False, False, Status.COMPLETED],
        [Error(ErrorType.BUSINESS, uuid4().hex), False, False, False, True, Status.COMPLETED],
        [None, True, False, False, False, Status.VALIDATION],
        [None, False, True, False, False, Status.NEEDS_REVIEW],
        [None, False, False, True, False, Status.EXPORTING],
        [None, False, False, False, False, Status.COMPLETED],
    ],
)
def test_postprocessing(
    error,
    needs_validation,
    needs_user_verification,
    needs_output_exporting,
    exceptional_queue_enabled,
    expected_status,
):
    s = StepFactory(
        needs_validation=needs_validation,
        needs_user_verification=needs_user_verification,
        needs_output_exporting=needs_output_exporting,
        exceptional_queue_enabled=exceptional_queue_enabled,
        error=error,
    ).make_postprocessing_step()

    ns = s.next_step()

    assert expected_status == ns.status
