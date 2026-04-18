from uuid import uuid4

import pytest
from deps_message_flow.commands.common import CommandReplyOutcome
from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)

from deps_workflow_manager.domain.model import WorkflowConfiguration
from deps_workflow_manager.messaging.commands import GetDocumentTypesReply
from deps_workflow_manager.messaging.events import (
    DocumentTypeUpdated,
    ExtractorAttached,
)


@pytest.fixture
def import_document_command_message(mocker):
    cm = mocker.Mock(CommandMessage)
    cm.command.document_name = uuid4().hex
    cm.command.document_metadata = {"extension": "jpeg"}
    cm.command.file_path = uuid4().hex
    cm.command.document_type = uuid4().hex
    cm.command.invoke_unifier = True
    cm.command.invoke_extraction = True
    cm.command.parsing_features = None
    cm.command.language = None
    cm.command.engine = None
    cm.command.llm_type = None
    return cm


@pytest.fixture
def document_type_updated_dee(
    mocker,
    test_tenant,
    document_type_id,
    llm_type,
    engine,
):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = DocumentTypeUpdated(
        document_type=document_type_id,
        tenant=test_tenant,
        llm_type=llm_type,
        engine=engine,
    )
    return dee


@pytest.fixture
def get_document_types_reply_cm(
    mocker,
    tenant_id,
    document_type_id,
    extraction_type,
    image_transformations,
    llm_type,
    engine,
):
    cm = mocker.Mock(CommandMessage)
    cm.message.get_required_header.return_value = CommandReplyOutcome.SUCCESS.name
    cm.command = GetDocumentTypesReply(
        [
            {
                "tenant_id": tenant_id,
                "document_type_id": document_type_id,
                "extraction_type": extraction_type,
                "image_transformations": image_transformations,
                "llm_type": llm_type,
                "engine": engine,
            }
        ]
    )

    return cm


@pytest.fixture
def failed_get_document_types_reply_cm(mocker):
    cm = mocker.Mock(CommandMessage)
    cm.message.get_required_header.return_value = CommandReplyOutcome.FAILURE.name

    return cm


@pytest.fixture
def extractor_attached_dee(
    mocker,
    document_type_id,
    extraction_type,
    image_transformations,
    engine,
):
    dee = mocker.Mock(DomainEventEnvelope)
    dee.event = ExtractorAttached(
        document_type_id=document_type_id,
        extraction_type=extraction_type,
        image_transformations=image_transformations,
        engine=engine,
    )
    return dee


@pytest.fixture
def workflow_configuration(test_tenant, document_type_id):
    return WorkflowConfiguration(tenant_id=test_tenant, document_type_id=document_type_id)


@pytest.fixture
def save_workflow_configuration(workflow_configuration_repository, workflow_configuration):
    workflow_configuration_repository.save(workflow_configuration)
