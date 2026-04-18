from unittest import mock
from uuid import uuid4

import pytest
from deps_message_flow.sagas.testing_support import *

from deps_workflow_manager.constants import (
    COMMANDS_CHANNEL,
    DOCUMENT_IMPORT_SERVICE_CHANNEL,
)
from deps_workflow_manager.domain.constants import ImportSource
from deps_workflow_manager.messaging.commands import (
    ImportDocuments,
    ImportDocumentsReply,
    ProcessDocuments,
)
from deps_workflow_manager.messaging.sagas import DocumentsImportSaga
from deps_workflow_manager.messaging.sagas_data import DocumentsImportSagaData


@pytest.mark.document_import
def test_plugin_document_import_saga():
    paths = [str(uuid4())]
    source = ImportSource.GOOGLE_DRIVE
    document_type_id = str(uuid4())
    documents = [[str(uuid4()), str(uuid4())]]
    tenant_id = str(uuid4())

    sd = DocumentsImportSagaData(
        paths=paths,
        source=source,
        document_type_id=document_type_id,
        tenant_id=tenant_id,
    )

    suts = (
        SagaUnitTestSupport.given()
        .saga(
            DocumentsImportSaga(),
            sd,
        )
        .expect()
        .command(ImportDocuments(paths=paths, source=source))
        .to(DOCUMENT_IMPORT_SERVICE_CHANNEL)
        .and_given()
        .success_reply(ImportDocumentsReply(documents=documents))
        .expect()
        .command(
            ProcessDocuments(
                documents=documents,
                document_type_id=document_type_id,
                tenant_id=tenant_id,
            )
        )
        .to(COMMANDS_CHANNEL)
        .and_given()
        .success_reply()
        .expect_completed_successfully()
    )
    saga_data = suts.saga_data

    assert saga_data["documents"] == documents
