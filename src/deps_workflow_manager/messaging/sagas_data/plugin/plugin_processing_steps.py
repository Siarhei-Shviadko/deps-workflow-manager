import logging

from deps_workflow_manager.domain.exceptions import RestClientError
from deps_workflow_manager.infrastructure.services import DocumentService

from .plugin_processing import PluginProcessingSagaData

__all__ = ["PluginProcessingSteps"]


class PluginProcessingSteps:
    def __init__(self, document_service: DocumentService):
        self._document_service = document_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document(self, data: PluginProcessingSagaData) -> None:
        if not data.is_invoke_document_creation():
            return

        try:
            data.update_next_state()

            self._logger.info(
                f"Creating document with "
                f"document_name={data.document_name}, "
                f"document_type_id={data.document_type_id}, "
                f"engine={data.engine}, "
                f"language={data.language}",
            )

            data.document_id = self._document_service.create_document(
                document_name=data.document_name,
                files=data.files,
                document_type_id=data.document_type_id,
                engine=data.engine,
                language=data.language,
                assign_to_me=data.assign_to_me,
                metadata=data.metadata,
            )

            self._logger.info(f"Created document {data.document_id}")

        except RestClientError as err:
            self._logger.error(f"Can't create document {data.document_name}. {str(err)}", exc_info=True)
            raise
