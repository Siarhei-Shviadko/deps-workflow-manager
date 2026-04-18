from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.unification_step
@pytest.mark.parametrize(
    "document_type,classification_enabled,needs_image_preprocessing,needs_parsing,needs_extraction,error,needs_exceptional_queue,expected_output",
    [
        [uuid4().hex, True, False, False, True, Error(ErrorType.SYSTEM, uuid4().hex), False, Status.FAILURE],
        [uuid4().hex, True, False, False, True, Error(ErrorType.BUSINESS, uuid4().hex), False, Status.POSTPONED],
        [uuid4().hex, True, False, False, True, Error(ErrorType.BUSINESS, uuid4().hex), True, Status.EXCEPTIONAL_QUEUE],
        [uuid4().hex, True, False, False, True, None, True, Status.EXTRACTION],
        [uuid4().hex, True, True, False, True, None, True, Status.IMAGE_PREPROCESSING],
        [uuid4().hex, True, False, True, True, None, True, Status.PARSING],
        [uuid4().hex, True, False, False, False, None, True, Status.COMPLETED],
        [None, True, False, False, False, None, True, Status.CLASSIFICATION],
        [None, False, False, False, False, None, True, Status.EXCEPTIONAL_QUEUE],
        [None, False, False, False, False, None, False, Status.POSTPONED],
    ],
)
def test_unification(
    document_type,
    classification_enabled,
    needs_image_preprocessing,
    needs_parsing,
    needs_extraction,
    error,
    needs_exceptional_queue,
    expected_output,
):
    s = StepFactory(
        document_type=document_type,
        classification_enabled=classification_enabled,
        needs_image_preprocessing=needs_image_preprocessing,
        needs_parsing=needs_parsing,
        needs_extraction=needs_extraction,
        error=error,
        needs_exceptional_queue=needs_exceptional_queue,
    ).make_unification_step()

    ns = s.next_step()

    assert expected_output == ns.status
