import pytest

from deps_workflow_manager.domain.exceptions import WorkflowManagerException
from deps_workflow_manager.domain.model import (
    CanRunPipelineSpecification,
    DocumentState,
)
from tests.factories import DocumentFactory


def test_can_run_pipeline_specification__satisfied():
    document = DocumentFactory(state=DocumentState.NEW)

    assert CanRunPipelineSpecification.is_satisfied_by(document)

    CanRunPipelineSpecification([document]).check()


@pytest.mark.parametrize(
    "state",
    [
        DocumentState.PREPROCESSING,
        DocumentState.DATA_EXTRACTION,
        DocumentState.VALIDATION,
        DocumentState.COMPLETED,
        DocumentState.FAILED,
        DocumentState.IDENTIFICATION,
        DocumentState.IN_REVIEW,
    ],
)
def test_can_run_pipeline_specification__not_satisfied(state):
    document = DocumentFactory(state=state)

    assert not CanRunPipelineSpecification.is_satisfied_by(document)

    with pytest.raises(WorkflowManagerException):
        CanRunPipelineSpecification([document]).check()
