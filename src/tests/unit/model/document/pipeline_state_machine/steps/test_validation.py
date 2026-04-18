from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.validation_step
@pytest.mark.parametrize(
    "error,needs_user_verification,needs_output_exporting,needs_review_on_validation_failure,exceptional_queue_enabled,expected_status",
    [
        [Error(ErrorType.SYSTEM, uuid4().hex), False, False, False, False, Status.COMPLETED],
        [Error(ErrorType.BUSINESS, uuid4().hex), False, False, False, False, Status.COMPLETED],
        [Error(ErrorType.BUSINESS, uuid4().hex), False, False, False, True, Status.COMPLETED],
        [Error(ErrorType.VALIDATION, uuid4().hex), False, False, True, False, Status.NEEDS_REVIEW],
        [Error(ErrorType.VALIDATION, uuid4().hex), False, True, False, False, Status.EXPORTING],
        [None, True, False, False, False, Status.NEEDS_REVIEW],
        [None, False, True, False, False, Status.EXPORTING],
        [None, False, False, False, False, Status.COMPLETED],
        [None, False, False, True, False, Status.COMPLETED],
        [None, False, True, True, False, Status.EXPORTING],
    ],
)
def test_validation(
    error,
    needs_user_verification,
    needs_output_exporting,
    needs_review_on_validation_failure,
    exceptional_queue_enabled,
    expected_status,
):
    s = StepFactory(
        needs_user_verification=needs_user_verification,
        needs_output_exporting=needs_output_exporting,
        exceptional_queue_enabled=exceptional_queue_enabled,
        needs_review_on_validation_failure=needs_review_on_validation_failure,
        error=error,
    ).make_validation_step()

    ns = s.next_step()

    assert expected_status == ns.status
