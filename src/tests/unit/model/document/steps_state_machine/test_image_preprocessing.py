from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.image_preprocessing_step
@pytest.mark.parametrize(
    "document_type,needs_parsing,needs_extraction,expected_output",
    [
        [None, True, False, Status.PARSING],
        [None, False, True, Status.COMPLETED],
        [uuid4().hex, False, False, Status.COMPLETED],
        [uuid4().hex, False, True, Status.EXTRACTION],
        [uuid4().hex, True, True, Status.PARSING],
    ],
)
def test_image_preprocessing(
    document_type,
    needs_parsing,
    needs_extraction,
    expected_output,
):
    s = StepFactory(
        document_type=document_type,
        needs_parsing=needs_parsing,
        needs_extraction=needs_extraction,
    ).make_image_preprocessing_step()

    ns = s.next_step()

    assert ns.status == expected_output
