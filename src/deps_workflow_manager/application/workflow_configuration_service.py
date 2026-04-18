import logging

from deps_message_flow.commands.producer import CommandProducer

from deps_workflow_manager.constants import COMMANDS_CHANNEL, COMMANDS_REPLIES_CHANNEL
from deps_workflow_manager.domain.exceptions import WorkflowConfigurationNotFound
from deps_workflow_manager.domain.model import (
    DocumentTypeInfo,
    IWorkflowConfigurationRepository,
    NeedsReviewOption,
    ParsingFeature,
    WorkflowConfiguration,
)
from deps_workflow_manager.messaging.commands import GetDocumentTypes

__all__ = ["WorkflowConfigurationService"]


class WorkflowConfigurationService:
    def __init__(
        self,
        workflow_configuration_repository: IWorkflowConfigurationRepository,
        command_producer: CommandProducer,
    ) -> None:
        self._command_producer = command_producer
        self._workflow_configuration_repository = workflow_configuration_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def initialize(self) -> None:
        self._command_producer.send(
            COMMANDS_CHANNEL,
            GetDocumentTypes(),
            COMMANDS_REPLIES_CHANNEL,
        )
        self._logger.info("Command GetDocumentTypes sent")

    def get_configuration(self, document_type_id: str, tenant_id: str) -> WorkflowConfiguration:
        if configuration := self.find_configuration(tenant_id, document_type_id):
            return configuration

        raise WorkflowConfigurationNotFound(
            f"Workflow configuration for document type `{document_type_id}` is not found",
        )

    def find_configuration(self, tenant_id: str, document_type_id: str) -> WorkflowConfiguration | None:
        return self._workflow_configuration_repository.find(
            tenant_id=tenant_id,
            document_type_id=document_type_id,
        )

    def find_all_configurations(self, tenant_id: str) -> list[WorkflowConfiguration]:
        return self._workflow_configuration_repository.find_all(tenant_id=tenant_id)

    def save_configuration(self, configuration: WorkflowConfiguration) -> None:
        self._workflow_configuration_repository.save(configuration=configuration)

    def save_configuration_for(self, document_types: list[DocumentTypeInfo]) -> None:
        self._workflow_configuration_repository.save_for(document_types=document_types)

    def delete_configuration(self, tenant_id: str, document_type_id: str) -> None:
        self._workflow_configuration_repository.delete(tenant_id=tenant_id, document_type_id=document_type_id)

    def update_configuration(
        self,
        tenant_id: str,
        document_type_id: str,
        llm_type: str | None = None,
        engine: str | None = None,
        parsing_features: set[ParsingFeature] | None = None,
        needs_extraction: bool | None = None,
        needs_postprocessing: bool | None = None,
        needs_validation: bool | None = None,
        needs_review: NeedsReviewOption | None = None,
        needs_output_exporting: bool | None = None,
    ) -> None:
        configuration = self.find_configuration(tenant_id, document_type_id)

        if configuration is None:
            raise WorkflowConfigurationNotFound(
                f"Workflow configuration for document type `{document_type_id}` is not found",
            )

        if llm_type is not None:
            configuration.llm_type = llm_type
        if engine is not None:
            configuration.engine = engine
        if parsing_features is not None:
            configuration.parsing_features = parsing_features
        if needs_extraction is not None:
            configuration.needs_extraction = needs_extraction
        if needs_postprocessing is not None:
            configuration.needs_postprocessing = needs_postprocessing
        if needs_validation is not None:
            configuration.needs_validation = needs_validation
        if needs_review is not None:
            configuration.needs_user_verification = needs_review.needs_user_verification
            configuration.needs_review_on_validation_failure = needs_review.needs_review_on_validation_failure

        if needs_output_exporting is not None:
            configuration.needs_output_exporting = needs_output_exporting

        self.save_configuration(configuration)
