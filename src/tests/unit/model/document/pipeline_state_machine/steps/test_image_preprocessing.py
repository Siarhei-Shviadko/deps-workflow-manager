from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.image_preprocessing_step
@pytest.mark.parametrize(
    (
        "document_type_id,"
        "error,"
        "needs_parsing,"
        "needs_version_classification,"
        "needs_extraction,"
        "needs_postprocessing,"
        "needs_validation,"
        "needs_user_verification,"
        "needs_output_exporting,"
        "classification_enabled,"
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
            False,
            False,
            False,
            Status.COMPLETED,
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
            False,
            False,
            False,
            Status.COMPLETED,
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
            False,
            False,
            True,
            Status.COMPLETED,
        ],
        [None, None, True, False, False, False, False, False, False, False, False, Status.PARSING],
        [None, None, False, False, False, False, False, False, False, True, False, Status.CLASSIFICATION],
        [None, None, False, False, False, False, False, False, False, False, False, Status.COMPLETED],
        [
            uuid4().hex,
            Error(ErrorType.SYSTEM, uuid4().hex),
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            Status.COMPLETED,
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
            False,
            False,
            False,
            Status.COMPLETED,
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
            False,
            False,
            True,
            Status.COMPLETED,
        ],
        [uuid4().hex, None, True, False, False, False, False, False, False, False, False, Status.PARSING],
        [
            uuid4().hex,
            None,
            False,
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            Status.VERSION_CLASSIFICATION,
        ],
        [uuid4().hex, None, False, False, True, False, False, False, False, False, False, Status.EXTRACTION],
        [uuid4().hex, None, False, False, False, True, False, False, False, False, False, Status.POSTPROCESSING],
        [uuid4().hex, None, False, False, False, False, True, False, False, False, False, Status.VALIDATION],
        [uuid4().hex, None, False, False, False, False, False, True, False, False, False, Status.NEEDS_REVIEW],
        [uuid4().hex, None, False, False, False, False, False, False, True, False, False, Status.EXPORTING],
        [uuid4().hex, None, False, False, False, False, False, False, False, False, False, Status.COMPLETED],
    ],
)
def test_image_preprocessing(
    document_type_id,
    error,
    needs_parsing,
    needs_version_classification,
    needs_extraction,
    needs_postprocessing,
    needs_validation,
    needs_user_verification,
    needs_output_exporting,
    classification_enabled,
    exceptional_queue_enabled,
    expected_status,
):
    s = StepFactory(
        document_type_id=document_type_id,
        needs_parsing=needs_parsing,
        needs_version_classification=needs_version_classification,
        needs_extraction=needs_extraction,
        needs_postprocessing=needs_postprocessing,
        needs_validation=needs_validation,
        needs_user_verification=needs_user_verification,
        needs_output_exporting=needs_output_exporting,
        classification_enabled=classification_enabled,
        exceptional_queue_enabled=exceptional_queue_enabled,
        error=error,
    ).make_image_preprocessing_step()

    ns = s.next_step()

    assert expected_status == ns.status
