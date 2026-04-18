from uuid import uuid4

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from deps_workflow_manager.entrypoint import create_fastapi
from deps_workflow_manager.infrastructure.context_vars import user


@pytest.fixture(scope="session")
def app() -> FastAPI:
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def session_containers(app):
    return app.containers


@pytest.fixture
def containers(session_containers):
    with session_containers.reset_singletons():
        yield session_containers


@pytest.fixture
def repositories(containers):
    return containers.repositories


@pytest.fixture
def test_command_channel():
    return "test-command-channel"


@pytest.fixture
def config(containers):
    return containers.config


@pytest.fixture
def test_tenant():
    return "Test tenant"


@pytest.fixture
def this_user(test_tenant):
    return dict(
        subject="VelvetKey",
        groups=[test_tenant],
        token="token",
        roles=["Colon"],
        organisation=test_tenant,
    )


@pytest.fixture
def other_organisation_user():
    return dict(subject="TestKey", groups=["OtherORG"], token="fakenToken", roles=["testRole"], organisation="OtherORG")


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture
def tenant_id():
    return uuid4().hex


@pytest.fixture
def document_type_id():
    return uuid4().hex
