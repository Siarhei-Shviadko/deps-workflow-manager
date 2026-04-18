from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.classification_step
@pytest.mark.parametrize(
    "document_type,needs_image_preprocessing,needs_parsing,needs_extraction,error,needs_exceptional_queue,expected_output",
    [
        [None, False, False, True, Error(ErrorType.BUSINESS, uuid4().hex), True, Status.EXCEPTIONAL_QUEUE],
        [None, False, False, True, Error(ErrorType.BUSINESS, uuid4().hex), False, Status.POSTPONED],
        [None, False, False, True, Error(ErrorType.SYSTEM, uuid4().hex), False, Status.FAILURE],
        [None, True, True, True, None, False, Status.IMAGE_PREPROCESSING],
        [None, False, True, True, None, False, Status.PARSING],
        [None, False, False, True, None, False, Status.COMPLETED],
        [None, False, False, False, None, False, Status.COMPLETED],
        [uuid4().hex, False, False, True, None, False, Status.EXTRACTION],
        [uuid4().hex, False, False, False, None, False, Status.COMPLETED],
    ],
)
def test_classification(
    document_type,
    needs_image_preprocessing,
    needs_parsing,
    needs_extraction,
    error,
    needs_exceptional_queue,
    expected_output,
):
    s = StepFactory(
        document_type=document_type,
        needs_image_preprocessing=needs_image_preprocessing,
        needs_parsing=needs_parsing,
        needs_extraction=needs_extraction,
        error=error,
        needs_exceptional_queue=needs_exceptional_queue,
    ).make_classification_step()

    ns = s.next_step()

    assert expected_output == ns.status
