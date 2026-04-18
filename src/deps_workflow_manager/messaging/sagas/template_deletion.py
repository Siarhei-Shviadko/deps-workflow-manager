import logging

from deps_message_flow.sagas.orchestration_simple_dsl import SimpleSaga

from deps_workflow_manager.messaging.exceptions import SagaFailed, SagaRolledBack

__all__ = ["TemplateDeletionSaga"]

from ..sagas_data.template.template_deletion_data import TemplateDeletionSagaData
from ..sagas_data.template.template_deletion_steps import TemplateDeletionSteps


class TemplateDeletionSaga(SimpleSaga[TemplateDeletionSagaData]):
    def __init__(self, steps: TemplateDeletionSteps) -> None:
        # fmt: off
        self._saga_definition = (
            self.step()
            .invoke_local(steps.check_doc_type_has_docs)
            .step()
            .invoke_local(steps.delete_template)
            .build()
        )
        # fmt: on
        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: TemplateDeletionSagaData) -> None:
        self._logger.info("Saga: %s for template %s deletion is completed successfully", saga_id, data.template_id)

    def on_saga_rolled_back(self, saga_id: str, data: TemplateDeletionSagaData) -> None:
        self._logger.warning("Saga: %s for template %s deletion is rolled back", saga_id, data.template_id)
        raise SagaRolledBack("Template deletion saga failed and rolled back")

    def on_saga_failed(self, saga_id: str, data: TemplateDeletionSagaData) -> None:
        self._logger.error("Saga: %s for template %s deletion is failed", saga_id, data.template_id)
        raise SagaFailed("Template deletion saga failed")
