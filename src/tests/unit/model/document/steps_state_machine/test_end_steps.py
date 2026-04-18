from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status, StepFactory


@pytest.mark.processing_steps
def test_exceptional_queue():
    s = StepFactory(
        document_type=uuid4().hex,
        error=Error(ErrorType.BUSINESS, uuid4().hex),
        needs_exceptional_queue=True,
    ).make_business_failed_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.EXCEPTIONAL_QUEUE == s.status


@pytest.mark.processing_steps
def test_postponed():
    s = StepFactory(
        document_type=uuid4().hex,
        error=Error(ErrorType.BUSINESS, uuid4().hex),
        needs_exceptional_queue=False,
    ).make_business_failed_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.POSTPONED == s.status


@pytest.mark.processing_steps
def test_failure():
    s = StepFactory(
        document_type=uuid4().hex,
        error=Error(ErrorType.SYSTEM, uuid4().hex),
    ).make_system_failed_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.FAILURE == s.status


@pytest.mark.processing_steps
def test_manual_review():
    s = StepFactory(
        document_type=uuid4().hex,
    ).make_manual_review_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.NEEDS_REVIEW == s.status


@pytest.mark.processing_steps
def test_successful():
    s = StepFactory(
        document_type=uuid4().hex,
    ).make_successful_processing_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.COMPLETED == s.status
