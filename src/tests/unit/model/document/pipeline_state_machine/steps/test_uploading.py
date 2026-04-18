from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Error, ErrorType, Status
from deps_workflow_manager.domain.model.document.pipeline_state_machine import (
    StepFactory,
)


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_uploading__error():
    s = StepFactory(
        document_type_id=uuid4().hex,
        needs_unification=False,
        error=Error(ErrorType.SYSTEM, message=uuid4().hex),
    ).make_uploading_step()

    ns = s.next_step()

    assert Status.FAILURE == ns.status


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_uploading__needs_unification():
    s = StepFactory(document_type_id=uuid4().hex, needs_unification=True).make_uploading_step()

    ns = s.next_step()

    assert Status.UNIFICATION == ns.status


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_uploading__completed():
    s = StepFactory(document_type_id=uuid4().hex, needs_unification=False).make_uploading_step()

    ns = s.next_step()

    assert Status.COMPLETED == ns.status
