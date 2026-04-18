import logging

from deps_workflow_manager.domain.model import IWorkflowConfigurationRepository

from .full_processing import FullProcessingSagaData

__all__ = ["FullProcessingSteps"]


class FullProcessingSteps:
    def __init__(self, workflow_configuration_repository: IWorkflowConfigurationRepository) -> None:
        self._workflow_configuration_repository = workflow_configuration_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def set_processing_configuration(self, data: FullProcessingSagaData) -> None:
        if data.document_type_id is None:
            return

        data.set_workflow_configuration(
            self._workflow_configuration_repository.find(
                data.tenant_id,
                data.document_type_id,
            ),
        )
