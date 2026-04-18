from uuid import uuid4

import pytest

from tests.fakes.workflow_configuration_repository import (
    FakeWorkflowConfigurationRepository,
)


@pytest.fixture
def postgres_datasource_mock(mocker, containers):
    mock = mocker.Mock(containers.datasources.postgres_datasource())
    containers.datasources.postgres_datasource.override(mock)

    yield mock

    containers.datasources.reset_override()


@pytest.fixture(scope="function", autouse=True)
def command_producer(containers, mocker):
    command_producer = containers.command_producer.override(mocker.Mock(containers.command_producer.cls))
    yield command_producer
    containers.command_producer.reset_override()


@pytest.fixture
def extraction_type():
    return "template"


@pytest.fixture
def image_transformations():
    return ["rotate", "crop"]


@pytest.fixture
def llm_type():
    return uuid4().hex


@pytest.fixture
def engine():
    return uuid4().hex


@pytest.fixture(autouse=True)
def workflow_configuration_repository(containers):
    with containers.repositories.workflow_configuration.override(FakeWorkflowConfigurationRepository()) as wcr:
        yield wcr()
