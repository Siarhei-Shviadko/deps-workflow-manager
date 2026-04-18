import pytest

from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.model import (
    PROCESSING_STATES,
    CanRunPipelineFromStepSpecification,
    DocumentState,
)
from tests.factories import DocumentFactory


@pytest.mark.parametrize(
    "state",
    PROCESSING_STATES + (DocumentState.NEW,),
)
def test_can_run_pipeline_from_step_specification__not_satisfied(state):
    document = DocumentFactory(state=state)

    assert not CanRunPipelineFromStepSpecification.is_satisfied_by(document)

    with pytest.raises(WorkflowManagerException):
        CanRunPipelineFromStepSpecification([document]).check()


@pytest.mark.parametrize(
    "state",
    [
        DocumentState.VALIDATION,
        DocumentState.COMPLETED,
        DocumentState.FAILED,
        DocumentState.IN_REVIEW,
    ],
)
def test_can_run_pipeline_from_step_specification__satisfied(state):
    document = DocumentFactory(state=state)

    assert CanRunPipelineFromStepSpecification.is_satisfied_by(document)

    CanRunPipelineFromStepSpecification([document]).check()
