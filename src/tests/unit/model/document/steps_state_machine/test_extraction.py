from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.extraction_step
@pytest.mark.parametrize(
    "document_type,needs_postprocessing,needs_validation,needs_user_verification,error,expected_output",
    [
        [uuid4().hex, False, False, False, Error(ErrorType.SYSTEM, uuid4().hex), Status.FAILURE],
        [uuid4().hex, True, False, False, None, Status.POSTPROCESSING],
        [uuid4().hex, False, True, False, None, Status.VALIDATION],
        [uuid4().hex, False, False, True, None, Status.NEEDS_REVIEW],
        [uuid4().hex, False, False, False, None, Status.COMPLETED],
    ],
)
def test_extraction(
    document_type, needs_postprocessing, needs_validation, needs_user_verification, error, expected_output
):
    s = StepFactory(
        document_type=document_type,
        needs_postprocessing=needs_postprocessing,
        needs_validation=needs_validation,
        error=error,
        needs_user_verification=needs_user_verification,
    ).make_extraction_step()

    ns = s.next_step()

    assert expected_output == ns.status
