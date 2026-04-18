import logging

from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from deps_workflow_manager.messaging.exceptions import SagaFailed, SagaRolledBack

from ..sagas_data import (
    TemplateCreateFromSagaData,
    TemplateCreateFromSteps,
    TemplateCreationSagaData,
    TemplateCreationSteps,
)

__all__ = ["TemplateCreationSaga", "TemplateCreateFromSaga"]


class TemplateCreationSaga(SimpleSaga[TemplateCreationSagaData]):
    def __init__(self, steps: TemplateCreationSteps) -> None:
        self._saga_definition = (
            self.step()
            .invoke_local(steps.create_document_type)
            .with_compensation(steps.delete_document_type)
            .step()
            .invoke_local(steps.create_template)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: TemplateCreationSagaData) -> None:
        self._logger.info("Saga: %s for template %s creation is completed successfully", saga_id, data.template_id)

    def on_saga_rolled_back(self, saga_id: str, data: TemplateCreationSagaData) -> None:
        self._logger.warning("Saga: %s for template %s creation is rolled back", saga_id, data.template_id)
        raise SagaRolledBack("Template creation saga failed and rolled back")

    def on_saga_failed(self, saga_id: str, data: TemplateCreationSagaData) -> None:
        self._logger.error("Saga: %s for template %s creation is failed", saga_id, data.template_id)
        raise SagaFailed("Template creation saga failed")


class TemplateCreateFromSaga(SimpleSaga[TemplateCreateFromSagaData]):
    def __init__(self, steps: TemplateCreateFromSteps) -> None:
        self._saga_definition = (
            self.step()
            .invoke_local(steps.create_document_type)
            .with_compensation(steps.delete_document_type)
            .step()
            .invoke_local(steps.create_template_from)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: TemplateCreationSagaData) -> None:
        self._logger.info("Saga: %s for copying template %s is completed successfully", saga_id, data.src_template_id)

    def on_saga_rolled_back(self, saga_id: str, data: TemplateCreationSagaData) -> None:
        self._logger.warning("Saga: %s for copying template %s is rolled back", saga_id, data.src_template_id)

        if data.original_exc:
            raise data.original_exc

        raise SagaRolledBack("Template create from saga failed and rolled back")

    def on_saga_failed(self, saga_id: str, data: TemplateCreationSagaData) -> None:
        self._logger.error("Saga: %s for copying template %s is failed", saga_id, data.src_template_id)
        raise SagaFailed("Template create from saga failed")
