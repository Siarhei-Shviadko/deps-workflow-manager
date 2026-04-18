from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.messaging.commands import (
    AutoMarkupFailedReply,
    CreateVersion,
    CreateVersionReply,
    ImplementAutoMarkup,
    PreprocessReferencePage,
    PreprocessReferencePageReply,
)
from deps_workflow_manager.messaging.sagas import VersionCreationSaga
from deps_workflow_manager.messaging.sagas_data import VersionCreationSagaData


@pytest.mark.version_creation_saga
def test_version_creation_saga_auto_markup():
    template_id = str(uuid4())
    tenant_id = str(uuid4())
    name = str(uuid4())
    blob_names = [str(uuid4())]
    preprocessed_blob_names = [str(uuid4())]
    version_id = str(uuid4())

    sd = VersionCreationSagaData(
        tenant_id=tenant_id,
        template_id=template_id,
        name=name,
        original_blob_names=blob_names,
        markup_automatically=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            VersionCreationSaga(),
            sd,
        )
        .expect()
        .command(PreprocessReferencePage(template_id, blob_names))
        .to("ImagePreprocessCommands")
        .and_given()
        .success_reply(PreprocessReferencePageReply(template_id, preprocessed_blob_names))
        .expect()
        .command(
            CreateVersion(
                template_id=template_id,
                tenant_id=tenant_id,
                name=name,
                original_blob_names=blob_names,
                preprocessed_blob_names=preprocessed_blob_names,
                description=None,
            )
        )
        .to("TemplateCommands")
        .and_given()
        .success_reply(CreateVersionReply(template_id, name, version_id))
        .expect()
        .command(ImplementAutoMarkup(template_id, version_id, tenant_id))
        .to("TemplateCommands")
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert saga_data["preprocessed_blob_names"] == preprocessed_blob_names
    assert saga_data["version_id"] == version_id


@pytest.mark.version_creation_saga
def test_version_creation_saga_auto_markup_failed():
    template_id = str(uuid4())
    tenant_id = str(uuid4())
    name = str(uuid4())
    blob_names = [str(uuid4())]
    preprocessed_blob_names = [str(uuid4())]
    version_id = str(uuid4())

    sd = VersionCreationSagaData(
        tenant_id=tenant_id,
        template_id=template_id,
        name=name,
        original_blob_names=blob_names,
        markup_automatically=True,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            VersionCreationSaga(),
            sd,
        )
        .expect()
        .command(PreprocessReferencePage(template_id, blob_names))
        .to("ImagePreprocessCommands")
        .and_given()
        .success_reply(PreprocessReferencePageReply(template_id, preprocessed_blob_names))
        .expect()
        .command(
            CreateVersion(
                template_id=template_id,
                tenant_id=tenant_id,
                name=name,
                original_blob_names=blob_names,
                preprocessed_blob_names=preprocessed_blob_names,
                description=None,
            )
        )
        .to("TemplateCommands")
        .and_given()
        .success_reply(CreateVersionReply(template_id, name, version_id))
        .expect()
        .command(ImplementAutoMarkup(template_id, version_id, tenant_id))
        .to("TemplateCommands")
        .and_given()
        .failure_reply(AutoMarkupFailedReply())
        .expect_rolled_back()
    )
    saga_data = suts.saga_data

    assert saga_data["auto_markup_failed"]
