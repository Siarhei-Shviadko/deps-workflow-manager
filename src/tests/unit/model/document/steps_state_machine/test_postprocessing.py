from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.postprocessing_step
@pytest.mark.parametrize(
    "document_type,needs_validation,needs_user_verification,expected_output",
    [
        [uuid4().hex, True, False, Status.VALIDATION],
        [uuid4().hex, False, True, Status.NEEDS_REVIEW],
        [uuid4().hex, False, False, Status.COMPLETED],
    ],
)
def test_postprocessing(document_type, needs_validation, needs_user_verification, expected_output):
    s = StepFactory(
        document_type=document_type,
        needs_validation=needs_validation,
        needs_user_verification=needs_user_verification,
    ).make_postprocessing_step()

    ns = s.next_step()

    assert expected_output == ns.status
