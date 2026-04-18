from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.version_classification_step
@pytest.mark.parametrize(
    (
        "document_type_id,"
        "error,"
        "needs_extraction,"
        "needs_postprocessing,"
        "needs_validation,"
        "needs_user_verification,"
        "needs_output_exporting,"
        "exceptional_queue_enabled,"
        "expected_status"
    ),
    [
        [
            None,
            Error(ErrorType.SYSTEM, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            False,
            Status.FAILURE,
        ],
        [
            None,
            Error(ErrorType.BUSINESS, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            False,
            Status.POSTPONED,
        ],
        [
            None,
            Error(ErrorType.BUSINESS, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            True,
            Status.EXCEPTIONAL_QUEUE,
        ],
        [None, None, False, False, False, False, False, False, Status.COMPLETED],
        [
            uuid4().hex,
            Error(ErrorType.SYSTEM, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            False,
            Status.FAILURE,
        ],
        [
            uuid4().hex,
            Error(ErrorType.BUSINESS, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            False,
            Status.POSTPONED,
        ],
        [
            uuid4().hex,
            Error(ErrorType.BUSINESS, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            True,
            Status.EXCEPTIONAL_QUEUE,
        ],
        [uuid4().hex, None, True, False, False, False, False, False, Status.EXTRACTION],
        [uuid4().hex, None, False, True, False, False, False, False, Status.POSTPROCESSING],
        [uuid4().hex, None, False, False, True, False, False, False, Status.VALIDATION],
        [uuid4().hex, None, False, False, False, True, False, False, Status.NEEDS_REVIEW],
        [uuid4().hex, None, False, False, False, False, True, False, Status.EXPORTING],
        [uuid4().hex, None, False, False, False, False, False, False, Status.COMPLETED],
    ],
)
def test_version_classification(
    document_type_id,
    error,
    needs_extraction,
    needs_postprocessing,
    needs_validation,
    needs_user_verification,
    needs_output_exporting,
    exceptional_queue_enabled,
    expected_status,
):
    s = StepFactory(
        document_type_id=document_type_id,
        needs_extraction=needs_extraction,
        needs_postprocessing=needs_postprocessing,
        needs_validation=needs_validation,
        needs_user_verification=needs_user_verification,
        needs_output_exporting=needs_output_exporting,
        exceptional_queue_enabled=exceptional_queue_enabled,
        error=error,
    ).make_version_classification_step()

    ns = s.next_step()

    assert expected_status == ns.status
