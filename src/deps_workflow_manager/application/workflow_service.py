import logging
import pathlib
from typing import Any, List, Optional

from dependency_injector.wiring import Provide, inject
from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_workflow_manager.domain.constants import (
    ImportSource,
    PluginPipelineStep,
    TemplatePipelineStep,
)
from deps_workflow_manager.domain.model import (
    CanCompleteReviewSpecification,
    CanRetryLastStepSpecification,
    CanRunPipelineFromStepSpecification,
    CanRunPipelineSpecification,
    CanValidateSpecification,
    Document,
    DocumentState,
    FileData,
    ParsingFeature,
)
from deps_workflow_manager.extras.storage import StorageControllerService
from deps_workflow_manager.infrastructure.services import DocumentService
from deps_workflow_manager.messaging.sagas import (
    CompleteReviewSaga,
    DocumentsImportSaga,
    PluginProcessingSaga,
    TemplateCreateFromSaga,
    TemplateCreationSaga,
    TemplateProcessingSaga,
    ValidateSaga,
    VersionCreationSaga,
)
from deps_workflow_manager.messaging.sagas.template_deletion import TemplateDeletionSaga
from deps_workflow_manager.messaging.sagas_data import (
    CompleteReviewSagaData,
    DocumentsImportSagaData,
    PluginProcessingSagaData,
    TemplateCreateFromSagaData,
    TemplateCreationSagaData,
    TemplateProcessingSagaData,
    ValidateSagaData,
    VersionCreationSagaData,
)

__all__ = ["WorkflowService"]

from deps_workflow_manager.messaging.sagas_data.template.template_deletion_data import (
    TemplateDeletionSagaData,
)


class WorkflowService:
    def __init__(
        self,
        storage_proxy: StorageControllerService,
        document_service: DocumentService,
        sagas: List[Saga],
        saga_instance_factory: SagaInstanceFactory,
        validation_enabled: bool,
    ) -> None:
        self._storage_proxy = storage_proxy
        self._document_service = document_service
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory

        self._validation_enabled = validation_enabled

        self._logger = logging.getLogger(self.__class__.__name__)

    def run_plugin_pipeline(
        self,
        document_ids: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        invoke_unifier: bool = True,
        invoke_extraction: bool = True,
    ) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRunPipelineSpecification(documents).check()

        for document in documents:
            self._create_plugin_processing_saga(
                document=document,
                engine=engine,
                language=language,
                llm_type=llm_type,
                invoke_unifier=invoke_unifier,
                invoke_extraction=invoke_extraction,
                next_state=DocumentState.PREPROCESSING,
            )

    def run_template_pipeline(
        self,
        document_ids: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        invoke_unifier: bool = True,
        invoke_preprocessor: bool = True,
        invoke_version_classification: bool = Provide["config.version_classification_enabled"],
        invoke_extraction: bool = True,
    ) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRunPipelineSpecification(documents).check()

        for document in documents:
            self._create_template_processing_saga(
                document=document,
                engine=engine,
                language=language,
                invoke_unifier=invoke_unifier,
                invoke_preprocessor=invoke_preprocessor,
                invoke_version_classification=invoke_version_classification,
                invoke_extraction=invoke_extraction,
                next_state=DocumentState.PREPROCESSING,
            )

    def run_plugin_pipeline_from_step(
        self,
        document_ids: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        invoke_unifier: bool = True,
        invoke_extraction: bool = True,
        step: PluginPipelineStep = PluginPipelineStep.PREPROCESS,
    ) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRunPipelineFromStepSpecification(documents).check()

        for document in documents:
            self._create_plugin_processing_saga(
                document=document,
                engine=engine,
                language=language,
                llm_type=llm_type,
                invoke_unifier=invoke_unifier,
                invoke_extraction=invoke_extraction,
                next_state=self._get_document_state_by_plugin_pipeline_step(step),
            )

    def run_template_pipeline_from_step(
        self,
        document_ids: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        invoke_unifier: bool = True,
        invoke_preprocessor: bool = True,
        invoke_version_classification: bool = Provide["config.version_classification_enabled"],
        invoke_extraction: bool = True,
        step: TemplatePipelineStep = TemplatePipelineStep.PREPROCESS,
    ) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRunPipelineFromStepSpecification(documents).check()

        for document in documents:
            self._create_template_processing_saga(
                document=document,
                engine=engine,
                language=language,
                invoke_unifier=invoke_unifier,
                invoke_preprocessor=invoke_preprocessor,
                invoke_version_classification=invoke_version_classification,
                invoke_extraction=invoke_extraction,
                next_state=self._get_document_state_by_template_pipeline_step(step),
            )

    def retry_plugin_pipeline_last_step(self, document_ids: list[str]) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRetryLastStepSpecification(documents).check()

        for document in documents:
            self._create_plugin_processing_saga(
                document=document,
                next_state=document.error_in_state,
            )

    def retry_template_pipeline_last_step(
        self,
        document_ids: list[str],
        invoke_version_classification: bool = Provide["config.version_classification_enabled"],
    ) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRetryLastStepSpecification(documents).check()

        for document in documents:
            self._create_template_processing_saga(
                document=document,
                invoke_version_classification=invoke_version_classification,
                next_state=document.error_in_state,
            )

    def process_via_plugin(
        self,
        document_name: str,
        document_type_id: str,
        engine: str,
        language: str,
        file_name: str,
        file: bytes,
        invoke_unifier: bool,
        invoke_extraction: bool,
        assign_to_me: bool,
        metadata: dict[str, Any] = None,
        llm_type: Optional[str] = None,
    ) -> str:
        blob_name = self._storage_proxy.upload_content(file_path=file_name, content=file)

        sd = PluginProcessingSagaData(
            document_name=self.DocumentName(document_name).clear_name,
            document_type_id=document_type_id,
            engine=engine,
            language=language,
            llm_type=llm_type,
            files=[blob_name],
            invoke_unifier=invoke_unifier,
            invoke_extraction=invoke_extraction,
            invoke_validation=self._validation_enabled,
            assign_to_me=assign_to_me,
            metadata=metadata,
        )

        si = self._saga_instance_factory.create(
            self._sagas[PluginProcessingSaga],
            sd,
        )
        self._logger.info(
            "Saga %s for document %s with type %s is created",
            si.saga_id,
            document_name,
            document_type_id,
        )

        return sd.document_id

    @inject
    def process_via_template(
        self,
        document_name: str,
        document_type_id: str,
        engine: Optional[str],
        language: Optional[str],
        file_name: str,
        file: bytes,
        invoke_unifier: bool,
        invoke_preprocessor: bool,
        invoke_extraction: bool,
        assign_to_me: bool,
        metadata: dict[str, Any] = None,
        invoke_version_classification: bool = Provide["config.version_classification_enabled"],
    ) -> str:
        blob_name = self._storage_proxy.upload_content(file_path=file_name, content=file)

        sd = TemplateProcessingSagaData(
            document_name=self.DocumentName(document_name).clear_name,
            document_type_id=document_type_id,
            engine=engine,
            language=language,
            files=[blob_name],
            invoke_unifier=invoke_unifier,
            invoke_preprocessor=invoke_preprocessor,
            invoke_extraction=invoke_extraction,
            invoke_version_classification=invoke_version_classification,
            invoke_validation=self._validation_enabled,
            assign_to_me=assign_to_me,
            metadata=metadata,
        )

        si = self._saga_instance_factory.create(
            self._sagas[TemplateProcessingSaga],
            sd,
        )
        self._logger.info(
            "Saga %s for document %s with type %s is created",
            si.saga_id,
            document_name,
            document_type_id,
        )

        return sd.document_id

    def create_template(
        self,
        name: str,
        language: str,
        engine: str,
        tenant_id: str,
        description: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> str:
        sd = TemplateCreationSagaData(
            name=name,
            language=language,
            engine=engine,
            tenant_id=tenant_id,
            group_id=group_id,
            description=description,
        )
        self._saga_instance_factory.create(
            self._sagas[TemplateCreationSaga],
            sd,
        )
        return sd.template_id

    def create_template_from(
        self,
        src_template_id: str,
        name: str,
        language: str,
        engine: str,
        tenant_id: str,
        description: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> str:
        sd = TemplateCreateFromSagaData(
            src_template_id=src_template_id,
            name=name,
            language=language,
            engine=engine,
            tenant_id=tenant_id,
            group_id=group_id,
            description=description,
        )
        self._saga_instance_factory.create(
            self._sagas[TemplateCreateFromSaga],
            sd,
        )
        return sd.template_id

    def create_version(
        self,
        template_id: str,
        tenant_id: str,
        name: str,
        files: list[FileData],
        *,
        description: Optional[str] = None,
        markup_automatically: bool = False,
    ) -> None:
        blob_names = self._upload_files_to_storage(files)

        si = self._saga_instance_factory.create(
            self._sagas[VersionCreationSaga],
            VersionCreationSagaData(
                template_id=template_id,
                tenant_id=tenant_id,
                name=name,
                original_blob_names=blob_names,
                description=description,
                markup_automatically=markup_automatically,
            ),
        )
        self._logger.info(
            "Saga %s for template %s with name %s is created",
            si.saga_id,
            template_id,
            name,
        )

    def complete_review(self, document_id: str) -> dict[str, Any]:
        document = self._document_service.get_brief_documents_info([document_id])[0]

        CanCompleteReviewSpecification(document).check()

        si = self._saga_instance_factory.create(
            self._sagas[CompleteReviewSaga],
            CompleteReviewSagaData(
                document_id=document.id,
                document_type_id=document.type_id,
                metadata=document.metadata,
                current_state=document.state,
                next_state=DocumentState.VALIDATION,
                validation_failed_next_step=document.state,
            ),
        )
        self._logger.info(
            "Saga complete_review %s for document_id %s with type %s is created",
            si.saga_id,
            document.id,
            document.type_id,
        )

        return self._document_service.get_full_document_info(document_id)

    def validate(self, document_id: str) -> dict[str, Any]:
        document = self._document_service.get_brief_documents_info([document_id])[0]

        CanValidateSpecification(document).check()

        si = self._saga_instance_factory.create(
            self._sagas[ValidateSaga],
            ValidateSagaData(
                document_id=document.id,
                document_type_id=document.type_id,
                metadata=document.metadata,
                current_state=document.state,
                next_state=DocumentState.VALIDATION,
                validation_failed_next_step=document.state,
            ),
        )
        self._logger.info(
            "Saga validate %s for document_id %s with type %s is created",
            si.saga_id,
            document.id,
            document.type_id,
        )

        return self._document_service.get_full_document_info(document_id)

    def delete_template(self, template_id: str, tenant_id: str):
        self._saga_instance_factory.create(
            self._sagas[TemplateDeletionSaga],
            TemplateDeletionSagaData(
                template_id=template_id,
                tenant_id=tenant_id,
            ),
        )

    def import_documents(
        self,
        paths: list[str],
        source: ImportSource,
        tenant_id: str,
        document_type_id: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        invoke_unifier: bool = False,
        invoke_extraction: bool = False,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
    ) -> None:
        si = self._saga_instance_factory.create(
            self._sagas[DocumentsImportSaga],
            DocumentsImportSagaData(
                paths=paths,
                source=source,
                document_type_id=document_type_id,
                tenant_id=tenant_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                invoke_unifier=invoke_unifier,
                invoke_extraction=invoke_extraction,
                assign_to_me=assign_to_me,
                parsing_features=parsing_features,
            ),
        )
        self._logger.info("DocumentsImportSaga %s with type %s is created", si.saga_id, document_type_id)

    class DocumentName:
        def __init__(self, value: str) -> None:
            self._value = value

        @property
        def clear_name(self) -> str:
            return pathlib.Path(self._value).stem

    def _upload_files_to_storage(self, files: list[FileData]) -> list[str]:
        return [self._storage_proxy.upload_content(file_path=file.path, content=file.io) for file in files]

    def _create_plugin_processing_saga(
        self,
        document: Document,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        invoke_unifier: bool = True,
        invoke_extraction: bool = True,
        next_state: DocumentState = DocumentState.PREPROCESSING,
    ):
        si = self._saga_instance_factory.create(
            self._sagas[PluginProcessingSaga],
            PluginProcessingSagaData(
                document_id=document.id,
                document_name=document.title,
                document_type_id=document.type_id,
                engine=engine or document.engine,
                language=language or document.language,
                llm_type=llm_type or document.llm_type,
                files=document.files,
                invoke_unifier=invoke_unifier,
                invoke_extraction=invoke_extraction,
                current_state=document.state,
                next_state=next_state,
            ),
        )
        self._logger.info(
            "Saga %s for document %s with type %s is created",
            si.saga_id,
            document.title,
            document.type_id,
        )

    def _create_template_processing_saga(
        self,
        document: Document,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        invoke_unifier: bool = True,
        invoke_preprocessor: bool = True,
        invoke_extraction: bool = True,
        invoke_version_classification: bool = True,
        next_state: DocumentState = DocumentState.PREPROCESSING,
    ):
        si = self._saga_instance_factory.create(
            self._sagas[TemplateProcessingSaga],
            TemplateProcessingSagaData(
                document_id=document.id,
                document_name=document.title,
                document_type_id=document.type_id,
                engine=engine or document.engine,
                language=language or document.language,
                files=document.files,
                invoke_unifier=invoke_unifier,
                invoke_preprocessor=invoke_preprocessor,
                invoke_version_classification=invoke_version_classification,
                invoke_extraction=invoke_extraction,
                current_state=document.state,
                next_state=next_state,
            ),
        )
        self._logger.info(
            "Saga %s for document %s with type %s is created",
            si.saga_id,
            document.title,
            document.type_id,
        )

    @staticmethod
    def _get_document_state_by_plugin_pipeline_step(pipeline_step: PluginPipelineStep) -> DocumentState:
        mapping = {
            PluginPipelineStep.PREPROCESS: DocumentState.PREPROCESSING,
            PluginPipelineStep.EXTRACTION: DocumentState.DATA_EXTRACTION,
        }

        next_document_state = mapping.get(pipeline_step)

        if not next_document_state:
            raise RuntimeError(f"Document state for plugin pipeline step {pipeline_step} is not defined.")

        return next_document_state

    @staticmethod
    def _get_document_state_by_template_pipeline_step(pipeline_step: TemplatePipelineStep) -> DocumentState:
        mapping = {
            TemplatePipelineStep.PREPROCESS: DocumentState.PREPROCESSING,
            TemplatePipelineStep.IDENTIFICATION: DocumentState.IDENTIFICATION,
            TemplatePipelineStep.EXTRACTION: DocumentState.DATA_EXTRACTION,
        }

        next_document_state = mapping.get(pipeline_step)

        if not next_document_state:
            raise RuntimeError(f"Document state for template pipeline step {pipeline_step} is not defined.")

        return next_document_state
