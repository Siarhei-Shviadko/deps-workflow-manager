from uuid import uuid4

import pytest

from deps_workflow_manager.domain.model import Status, StepFactory


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_uploading__needs_unification():
    s = StepFactory(document_type=uuid4().hex).make_uploading_step()

    ns = s.next_step()

    assert Status.UNIFICATION == ns.status


@pytest.mark.processing_steps
@pytest.mark.uploading_step
def test_uploading__completed():
    s = StepFactory(document_type=uuid4().hex, needs_unification=False).make_uploading_step()

    ns = s.next_step()

    assert Status.COMPLETED == ns.status
