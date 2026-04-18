import json
from http import HTTPStatus

import pytest

from deps_workflow_manager import constants
from deps_workflow_manager.domain.model import NeedsReviewOption, WorkflowConfiguration
from deps_workflow_manager.infrastructure.repositories import (
    WorkflowConfigurationRepository,
)

URL = f"{constants.API_PREFIX}/workflow-configuration"


@pytest.mark.workflow_configuration
def test_update_workflow_configuration__configuration_doesnt_exist__404(
    client,
    tenant_id,
    document_type_id,
):
    headers = {"deps-token": json.dumps({"organisation": tenant_id})}
    res = client.patch(URL, headers=headers, json={"documentTypeId": document_type_id})

    assert res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.workflow_configuration
def test_update_workflow_configuration__configuration_exist_for_other_tenant__404(
    client,
    workflow_configuration: WorkflowConfiguration,
    workflow_configuration_repo: WorkflowConfigurationRepository,
):
    workflow_configuration_repo.save(workflow_configuration)
    headers = {"deps-token": json.dumps({"organisation": "other_tenant_id"})}
    res = client.patch(URL, headers=headers, json={"documentTypeId": workflow_configuration.document_type_id})

    assert res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.workflow_configuration
def test_update_workflow_configuration__configuration_exists__updated(
    client,
    workflow_configuration: WorkflowConfiguration,
    workflow_configuration_repo: WorkflowConfigurationRepository,
):
    assert workflow_configuration.needs_postprocessing is True
    assert workflow_configuration.needs_validation is True
    assert workflow_configuration.needs_user_verification is False
    assert workflow_configuration.needs_review_on_validation_failure is True
    workflow_configuration_repo.save(workflow_configuration)

    headers = {"deps-token": json.dumps({"organisation": workflow_configuration.tenant_id})}
    res = client.patch(
        URL,
        headers=headers,
        json={
            "documentTypeId": workflow_configuration.document_type_id,
            "needsPostprocessing": False,
            "needsValidation": False,
            "needsReview": NeedsReviewOption.NO_REVIEW,
        },
    )

    assert res.status_code == HTTPStatus.OK

    new_configuration = workflow_configuration_repo.find(
        workflow_configuration.tenant_id,
        workflow_configuration.document_type_id,
    )

    assert new_configuration.needs_postprocessing is False
    assert new_configuration.needs_validation is False
    assert new_configuration.needs_user_verification is False


def test_get_workflow_configuration__configuration_exists__returns_configuration(
    client,
    workflow_configuration: WorkflowConfiguration,
    workflow_configuration_repo: WorkflowConfigurationRepository,
):
    workflow_configuration_repo.save(workflow_configuration)
    headers = {"deps-token": json.dumps({"organisation": workflow_configuration.tenant_id})}
    res = client.get(f"{URL}/{workflow_configuration.document_type_id}", headers=headers)

    assert res.status_code == HTTPStatus.OK

    res_json = res.json()

    assert res_json["needsPostprocessing"] == workflow_configuration.needs_postprocessing
    assert res_json["needsValidation"] == workflow_configuration.needs_validation
    assert res_json["needsReview"] == workflow_configuration.needs_review
    assert res_json["needsOutputExporting"] == workflow_configuration.needs_output_exporting
    assert res_json["parsingFeatures"] == list(workflow_configuration.parsing_features)
