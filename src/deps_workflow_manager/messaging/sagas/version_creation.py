import logging

from deps_message_flow.sagas.orchestration_simple_dsl import *

from ..commands import (
    AutoMarkupFailedReply,
    CreateVersionReply,
    PreprocessReferencePageReply,
)
from ..saga_handlers import VersionCreationHandlers
from ..sagas_data import VersionCreationSagaData

__all__ = ["VersionCreationSaga"]


class VersionCreationSaga(SimpleSaga[VersionCreationSagaData]):
    def __init__(self) -> None:
        self._saga_definition = (
            self.step()
            .invoke_participant(VersionCreationSagaData.preprocess_reference_pages)
            .on_reply(PreprocessReferencePageReply, VersionCreationHandlers.preprocess_reference_pages)
            .with_compensation(
                VersionCreationSagaData.delete_preprocessed_files,
                compensation_predicate=VersionCreationSagaData.should_delete_preprocessed_files,
            )
            .step()
            .invoke_participant(VersionCreationSagaData.create_version)
            .on_reply(CreateVersionReply, VersionCreationHandlers.create_version)
            .step()
            .invoke_participant(
                VersionCreationSagaData.implement_auto_markup,
                predicate=VersionCreationSagaData.should_implement_auto_markup,
            )
            .on_reply(AutoMarkupFailedReply, VersionCreationHandlers.auto_markup_failed)
            .build()
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    def on_saga_completed_successfully(self, saga_id: str, data: VersionCreationSagaData) -> None:
        self._logger.info("Saga: %s for template: %s is completed successfully", saga_id, data.template_id)

    def on_saga_failed(self, saga_id: str, data: VersionCreationSagaData) -> None:
        self._logger.info("Saga: %s for template: %s is failed", saga_id, data.template_id)

    def on_saga_rolled_back(self, saga_id: str, data: VersionCreationSagaData) -> None:
        self._logger.info("Saga: %s for template: %s is rolled back", saga_id, data.template_id)
