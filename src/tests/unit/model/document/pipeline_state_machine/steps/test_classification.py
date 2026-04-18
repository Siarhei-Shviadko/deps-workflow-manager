from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.classification_step
@pytest.mark.parametrize(
    "document_type_id,error,exceptional_queue_enabled,expected_status",
    [
        [None, Error(ErrorType.SYSTEM, uuid4().hex), False, Status.FAILURE],
        [None, Error(ErrorType.BUSINESS, uuid4().hex), False, Status.POSTPONED],
        [None, Error(ErrorType.BUSINESS, uuid4().hex), True, Status.EXCEPTIONAL_QUEUE],
        [None, None, False, Status.FAILURE],
        [uuid4().hex, Error(ErrorType.SYSTEM, uuid4().hex), False, Status.FAILURE],
        [uuid4().hex, Error(ErrorType.BUSINESS, uuid4().hex), False, Status.POSTPONED],
        [uuid4().hex, Error(ErrorType.BUSINESS, uuid4().hex), True, Status.EXCEPTIONAL_QUEUE],
        [uuid4().hex, None, False, Status.UNIFICATION],
    ],
)
def test_classification(
    document_type_id,
    error,
    exceptional_queue_enabled,
    expected_status,
):
    s = StepFactory(
        document_type_id=document_type_id,
        exceptional_queue_enabled=exceptional_queue_enabled,
        error=error,
    ).make_classification_step()

    ns = s.next_step()

    assert expected_status == ns.status
