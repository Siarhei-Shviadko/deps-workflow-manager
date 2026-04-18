import logging

from deps_workflow_manager.domain.exceptions import (
    NotFoundError,
    WorkflowManagerException,
)
from deps_workflow_manager.infrastructure.services import (
    DocumentTypeService,
    ExtractionService,
    TemplateService,
)

from .template_creation_data import TemplateCreateFromSagaData, TemplateCreationSagaData

__all__ = ["TemplateCreationSteps", "TemplateCreateFromSteps"]
TEMPLATE_EXTRACTOR_TYPE: str = "template"


class TemplateCreationSteps:
    def __init__(
        self,
        document_type_service: DocumentTypeService,
        template_service: TemplateService,
        extraction_service: ExtractionService,
    ):
        self._document_type_service = document_type_service
        self._template_service = template_service
        self._extraction_service = extraction_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document_type(self, data: TemplateCreationSagaData) -> None:
        self._logger.info(
            f"Creating document type with"
            f"name={data.name}, "
            f"extractor_type={TEMPLATE_EXTRACTOR_TYPE}, "
            f"language={data.language}, "
            f"engine={data.engine}",
        )
        try:
            document_type_id = self._extraction_service.create_document_type(
                name=data.name,
                language=data.language,
                engine=data.engine,
                description=data.description,
                extractor_type=TEMPLATE_EXTRACTOR_TYPE,
            )
        except WorkflowManagerException as exc:
            self._logger.error(f"Document type creation error. {str(exc)}", exc_info=True)
            raise
        except Exception as exc:
            self._logger.error(f"Unhandled error. {str(exc)}", exc_info=True)
            raise RuntimeError(str(exc))
        else:
            data.template_id = document_type_id

    def delete_document_type(self, data: TemplateCreationSagaData) -> None:
        self._logger.info(f"Deleting document type {data.template_id}")
        self._document_type_service.delete_document_type(data.template_id)

    def create_template(self, data: TemplateCreationSagaData) -> None:
        self._logger.info(f"Creating template {data.template_id} in template service")
        try:
            self._template_service.create_template(
                template_id=data.template_id,
                name=data.name,
                language=data.language,
                engine=data.engine,
                group_id=data.group_id,
                description=data.description,
            )
        except WorkflowManagerException as exc:
            self._logger.error(f"Template creation error. {str(exc)}", exc_info=True)
            raise
        except Exception as exc:
            self._logger.error(f"Unhandled error. {str(exc)}")
            raise RuntimeError(str(exc))


class TemplateCreateFromSteps:
    def __init__(
        self,
        document_type_service: DocumentTypeService,
        template_service: TemplateService,
        extraction_service: ExtractionService,
    ):
        self._document_type_service = document_type_service
        self._template_service = template_service
        self._extraction_service = extraction_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document_type(self, data: TemplateCreateFromSagaData) -> None:
        try:
            data.template_id = self._extraction_service.create_document_type(
                name=data.name,
                language=data.language,
                engine=data.engine,
                description=data.description,
                extractor_type=TEMPLATE_EXTRACTOR_TYPE,
            )
        except WorkflowManagerException as exc:
            self._logger.error(f"Document type creation error. {str(exc)}", exc_info=True)
            raise
        except Exception as exc:
            errmsg = str(exc)
            self._logger.error(f"Unhandled error. {errmsg}", exc_info=True)
            raise RuntimeError(errmsg)

    def delete_document_type(self, data: TemplateCreateFromSagaData) -> None:
        self._document_type_service.delete_document_type(data.template_id)

    def create_template_from(self, data: TemplateCreateFromSagaData) -> None:
        try:
            data.template_id = self._template_service.create_template_from(
                src_template_id=data.src_template_id,
                name=data.name,
                language=data.language,
                engine=data.engine,
                template_id=data.template_id,
                group_id=data.group_id,
                description=data.description,
            )
        except NotFoundError as exc:
            self._logger.error(f"Template creation error. {str(exc)}", exc_info=True)
            data.original_exc = NotFoundError(f"Template with ID '{data.src_template_id}' not found")
            # We need to raise the RuntimeError exception to rollback the saga
            raise RuntimeError(f"Template not found: {exc}") from exc
        except Exception as exc:
            self._logger.error(f"Unhandled error. {str(exc)}")
            raise RuntimeError(str(exc))
