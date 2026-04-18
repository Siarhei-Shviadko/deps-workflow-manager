import pytest

from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.model import (
    PROCESSING_STATES,
    CanRetryLastStepSpecification,
    DocumentState,
)
from tests.factories import DocumentFactory


@pytest.mark.parametrize(
    "state",
    PROCESSING_STATES,
)
def test_can_retry_last_step_specification__satisfied(state):
    document = DocumentFactory(error_in_state=state)

    assert CanRetryLastStepSpecification.is_satisfied_by(document)

    CanRetryLastStepSpecification([document]).check()


@pytest.mark.parametrize(
    "state",
    [
        DocumentState.VALIDATION,
        DocumentState.COMPLETED,
        DocumentState.FAILED,
        DocumentState.IN_REVIEW,
        None,
    ],
)
def test_can_retry_last_step_specification__not_satisfied(state):
    document = DocumentFactory(error_in_state=state)

    assert not CanRetryLastStepSpecification.is_satisfied_by(document)

    with pytest.raises(WorkflowManagerException):
        CanRetryLastStepSpecification([document]).check()
