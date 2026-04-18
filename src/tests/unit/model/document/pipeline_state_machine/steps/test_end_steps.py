from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
def test_exceptional_queue():
    s = StepFactory(
        error=Error(ErrorType.BUSINESS, uuid4().hex),
        exceptional_queue_enabled=True,
    ).make_failed_processing_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.EXCEPTIONAL_QUEUE == s.status


@pytest.mark.processing_steps
def test_postponement():
    s = StepFactory(
        error=Error(ErrorType.BUSINESS, uuid4().hex),
    ).make_failed_processing_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.POSTPONED == s.status


@pytest.mark.processing_steps
def test_failure():
    s = StepFactory(error=Error(ErrorType.SYSTEM, uuid4().hex)).make_failed_processing_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.FAILURE == s.status


@pytest.mark.processing_steps
def test_manual_review():
    s = StepFactory().make_manual_review_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.NEEDS_REVIEW == s.status


@pytest.mark.processing_steps
def test_successful_processing():
    s = StepFactory().make_successful_processing_step()

    with pytest.raises(RuntimeError):
        s.next_step()

    assert Status.COMPLETED == s.status
