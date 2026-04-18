from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.validation_step
@pytest.mark.parametrize(
    "document_type,needs_user_verification,expected_output",
    [
        [uuid4().hex, True, Status.NEEDS_REVIEW],
        [uuid4().hex, False, Status.COMPLETED],
    ],
)
def test_validation(document_type, needs_user_verification, expected_output):
    s = StepFactory(
        document_type=document_type,
        needs_user_verification=needs_user_verification,
    ).make_validation_step()

    ns = s.next_step()

    assert expected_output == ns.status
