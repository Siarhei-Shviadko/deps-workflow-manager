import logging
import pathlib
from typing import List, Optional

from deps_message_flow.sagas.orchestration import Saga, SagaInstanceFactory

from deps_workflow_manager.domain.model import (
    CanRunPipelineFromStepSpecification,
    Document,
    FileData,
    IDocumentProcessingInfoRepository,
    NeedsReviewOption,
    ParsingFeature,
    Status,
)
from deps_workflow_manager.domain.model.document_processing.pipeline_specification import (
    CanRetryLastStepSpecification,
    CanRunPipelineSpecification,
)
from deps_workflow_manager.extras.storage import StorageControllerService
from deps_workflow_manager.infrastructure.services import DocumentService
from deps_workflow_manager.messaging.sagas import (
    DocumentProcessingSaga,
    FullProcessingSaga,
    TypelessDocumentProcessingSaga,
)
from deps_workflow_manager.messaging.sagas_data import (
    DocumentProcessingSagaData,
    DocumentStatusStateMap,
    FullProcessingSagaData,
    TypelessDocumentProcessingSagaData,
)

__all__ = ["DocumentProcessingService"]

FIRST_ELEMENT = 0
RUN_PIPELINE_FIRST_STEP = Status.UNIFICATION


class DocumentProcessingService:
    def __init__(
        self,
        storage_proxy: StorageControllerService,
        document_service: DocumentService,
        sagas: List[Saga],
        saga_instance_factory: SagaInstanceFactory,
        document_processing_repository: IDocumentProcessingInfoRepository,
        version_classification_enabled: bool = False,
        classification_enabled: bool = False,
        exceptional_queue_enabled: bool = False,
    ) -> None:
        self._storage_proxy = storage_proxy
        self._document_service = document_service
        self._sagas = {saga.__class__: saga for saga in sagas}
        self._saga_instance_factory = saga_instance_factory

        self._version_classification_enabled = version_classification_enabled
        self._classification_enabled = classification_enabled
        self._exceptional_queue_enabled = exceptional_queue_enabled

        self._document_processing_repository = document_processing_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    def process_document(
        self,
        tenant_id: str,
        document_name: Optional[str] = None,
        document_id: Optional[str] = None,
        document_type_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        file_name: Optional[str] = None,
        file: Optional[bytes] = None,
        files: Optional[list[str]] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
        output_profile_ids: Optional[list[str]] = None,
        needs_unifier: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[NeedsReviewOption] = None,
        needs_output_exporting: Optional[bool] = None,
        document_metadata: Optional[dict] = None,
        current_status: Status = Status.NEW,
    ) -> None:
        if not files:
            if not file:
                raise RuntimeError("Please provide raw file with filename or files.")

            files = [self._storage_proxy.upload_content(file_path=file_name, content=file)]

        if document_type_id is None:
            self.start_typeless_document_processing(
                tenant_id=tenant_id,
                document_name=document_name,
                document_id=document_id,
                parent_id=parent_id,
                files=files,
                engine=engine,
                language=language,
                llm_type=llm_type,
                assign_to_me=assign_to_me,
                parsing_features=parsing_features,
                needs_unifier=needs_unifier,
                needs_extraction=needs_extraction,
                needs_parsing=needs_parsing,
                needs_user_verification=needs_review.needs_user_verification if needs_review else None,
                document_metadata=document_metadata,
                current_status=current_status,
            )
        else:
            self.start_document_processing(
                tenant_id=tenant_id,
                document_id=document_id,
                document_name=document_name,
                document_type_id=document_type_id,
                parent_id=parent_id,
                files=files,
                engine=engine,
                llm_type=llm_type,
                language=language,
                assign_to_me=assign_to_me,
                parsing_features=parsing_features,
                output_profile_ids=output_profile_ids,
                needs_unifier=needs_unifier,
                needs_extraction=needs_extraction,
                needs_parsing=needs_parsing,
                needs_validation=needs_validation,
                needs_user_verification=needs_review.needs_user_verification if needs_review else None,
                needs_output_exporting=needs_output_exporting,
                needs_review_on_validation_failure=needs_review.needs_review_on_validation_failure
                if needs_review
                else None,
                document_metadata=document_metadata,
                current_status=current_status,
            )

    def start_document_processing(
        self,
        tenant_id: str,
        files: list[str],
        document_type_id: str,
        document_name: Optional[str] = None,
        document_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
        output_profile_ids: Optional[list[str]] = None,
        needs_unifier: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_user_verification: Optional[bool] = None,
        needs_review_on_validation_failure: Optional[bool] = None,
        needs_output_exporting: Optional[bool] = None,
        document_metadata: Optional[dict] = None,
        current_status: Status = Status.NEW,
    ) -> None:
        saga_data = DocumentProcessingSagaData(
            tenant_id=tenant_id,
            document_name=self.DocumentName(document_name).clear_name if document_name else None,
            document_type_id=document_type_id,
            document_id=document_id,
            parent_id=parent_id,
            engine=engine,
            language=language,
            llm_type=llm_type,
            parsing_features=parsing_features,
            output_profile_ids=output_profile_ids,
            files=files,
            assign_to_me=assign_to_me,
            needs_unifier=needs_unifier,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_user_verification=needs_user_verification,
            needs_review_on_validation_failure=needs_review_on_validation_failure,
            needs_output_exporting=needs_output_exporting,
            exceptional_queue_enabled=self._exceptional_queue_enabled,
            version_classification_enabled=self._version_classification_enabled,
            document_metadata=document_metadata,
            current_status=current_status,
        )

        si = self._saga_instance_factory.create(
            self._sagas[DocumentProcessingSaga],
            saga_data,
        )
        self._logger.info(
            "Saga %s for document %s with type %s is created",
            si.saga_id,
            document_name,
            document_type_id,
        )

    def start_typeless_document_processing(
        self,
        tenant_id: str,
        files: list[str],
        document_name: Optional[str] = None,
        document_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
        language: Optional[str] = None,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unifier: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_user_verification: Optional[bool] = None,
        document_metadata: Optional[dict] = None,
        current_status: Status = Status.NEW,
    ) -> None:
        saga_data = TypelessDocumentProcessingSagaData(
            tenant_id=tenant_id,
            document_name=self.DocumentName(document_name).clear_name if document_name else None,
            document_id=document_id,
            parent_id=parent_id,
            engine=engine,
            language=language,
            llm_type=llm_type,
            parsing_features=parsing_features,
            files=files,
            assign_to_me=assign_to_me,
            needs_unifier=needs_unifier,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_user_verification=needs_user_verification,
            exceptional_queue_enabled=self._exceptional_queue_enabled,
            classification_enabled=self._classification_enabled,
            document_metadata=document_metadata,
            current_status=current_status,
        )

        si = self._saga_instance_factory.create(
            self._sagas[TypelessDocumentProcessingSaga],
            saga_data,
        )
        self._logger.info(
            "Typeless saga %s for document %s  is created",
            si.saga_id,
            document_name,
        )

    def full_process_document(
        self,
        tenant_id: str,
        document_name: str,
        file_name: str,
        document_type_id: Optional[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
        invoke_unifier: bool = False,
        invoke_extraction: bool = False,
        document_metadata: Optional[dict] = None,
    ) -> None:
        saga_data = FullProcessingSagaData(
            tenant_id=tenant_id,
            document_name=self.DocumentName(document_name).clear_name,
            document_type_id=document_type_id,
            engine=engine,
            language=language,
            llm_type=llm_type,
            parsing_features=parsing_features,
            files=[file_name],
            assign_to_me=assign_to_me,
            invoke_unifier=invoke_unifier,
            invoke_extraction=invoke_extraction,
            needs_exceptional_queue=self._exceptional_queue_enabled,
            invoke_classification=self._version_classification_enabled,
            document_metadata=document_metadata,
        )

        si = self._saga_instance_factory.create(
            self._sagas[FullProcessingSaga],
            saga_data,
        )

        self._logger.info(
            "Saga %s for document %s with type %s is created",
            si.saga_id,
            document_name,
            document_type_id,
        )

    def run_pipeline(
        self,
        document_id: str,
        tenant_id: str,
    ) -> None:
        document = self._get_document_brief_info(document_id)
        CanRunPipelineSpecification(document).check()

        processing_info = self._document_processing_repository.find(document_id=document_id, tenant_id=tenant_id)

        if document.type_id:
            self.start_document_processing(
                tenant_id=tenant_id,
                document_name=document.title,
                files=document.files,
                document_type_id=document.type_id,
                document_id=document.id,
                parent_id=document.parent_id,
                engine=document.engine,
                language=document.language,
                llm_type=document.llm_type,
                assign_to_me=processing_info.assign_to_me,
                parsing_features=processing_info.parsing_features,
                needs_unifier=processing_info.needs_unifier,
                needs_extraction=processing_info.needs_extraction,
                document_metadata=document.metadata,
                current_status=RUN_PIPELINE_FIRST_STEP,
            )
        else:
            self.start_typeless_document_processing(
                document_id=document.id,
                tenant_id=tenant_id,
                document_name=document.title,
                files=document.files,
                parent_id=document.parent_id,
                engine=document.engine,
                language=document.language,
                llm_type=document.llm_type,
                assign_to_me=processing_info.assign_to_me,
                parsing_features=processing_info.parsing_features,
                needs_unifier=processing_info.needs_unifier,
                needs_extraction=processing_info.needs_extraction,
                document_metadata=document.metadata,
                current_status=RUN_PIPELINE_FIRST_STEP,
            )

    def retry_pipeline_last_step(
        self,
        document_id: str,
        tenant_id: str,
    ) -> None:
        document = self._get_document_brief_info(document_id)
        CanRetryLastStepSpecification(document).check()

        processing_info = self._document_processing_repository.find(document_id=document_id, tenant_id=tenant_id)

        if document.type_id:
            self.start_document_processing(
                document_id=document_id,
                tenant_id=tenant_id,
                document_name=document.title,
                document_type_id=document.type_id,
                files=document.files,
                parent_id=document.parent_id,
                engine=document.engine,
                language=document.language,
                llm_type=document.llm_type,
                document_metadata=document.metadata,
                assign_to_me=processing_info.assign_to_me,
                parsing_features=processing_info.parsing_features,
                needs_unifier=processing_info.needs_unifier,
                needs_extraction=processing_info.needs_extraction,
                current_status=DocumentStatusStateMap.status_from_state(document.error_in_state),
            )
        else:
            self.start_typeless_document_processing(
                document_id=document_id,
                tenant_id=tenant_id,
                document_name=document.title,
                files=document.files,
                parent_id=document.parent_id,
                engine=document.engine,
                language=document.language,
                llm_type=document.llm_type,
                document_metadata=document.metadata,
                assign_to_me=processing_info.assign_to_me,
                parsing_features=processing_info.parsing_features,
                needs_unifier=processing_info.needs_unifier,
                needs_extraction=processing_info.needs_extraction,
                current_status=DocumentStatusStateMap.status_from_state(document.error_in_state),
            )

    def run_pipeline_from_step(
        self,
        document_ids: list[str],
        tenant_id: str,
        step: Status,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        parsing_features: Optional[set[ParsingFeature]] = None,
    ) -> None:
        documents = self._document_service.get_brief_documents_info(document_ids)

        CanRunPipelineFromStepSpecification(documents).check()

        for document in documents:
            processing_info = self._document_processing_repository.find(document_id=document.id, tenant_id=tenant_id)

            if document.type_id:
                self.start_document_processing(
                    document_id=document.id,
                    tenant_id=tenant_id,
                    document_name=document.title,
                    document_type_id=document.type_id,
                    files=document.files,
                    parent_id=document.parent_id,
                    engine=engine,
                    language=language,
                    llm_type=llm_type,
                    document_metadata=document.metadata,
                    assign_to_me=processing_info.assign_to_me,
                    parsing_features=parsing_features or processing_info.parsing_features,
                    needs_unifier=processing_info.needs_unifier,
                    needs_extraction=processing_info.needs_extraction,
                    current_status=step,
                )
            else:
                self.start_typeless_document_processing(
                    document_id=document.id,
                    tenant_id=tenant_id,
                    document_name=document.title,
                    files=document.files,
                    parent_id=document.parent_id,
                    engine=engine,
                    language=language,
                    llm_type=llm_type,
                    document_metadata=document.metadata,
                    assign_to_me=processing_info.assign_to_me,
                    parsing_features=parsing_features or processing_info.parsing_features,
                    needs_unifier=processing_info.needs_unifier,
                    needs_extraction=processing_info.needs_extraction,
                    current_status=step,
                )

    class DocumentName:
        def __init__(self, value: str) -> None:
            self._value = value

        @property
        def clear_name(self) -> str:
            return pathlib.Path(self._value).stem

    def _upload_files_to_storage(self, files: list[FileData]) -> list[str]:
        return [self._storage_proxy.upload_content(file_path=file.path, content=file.io) for file in files]

    def _get_document_brief_info(self, document_id: str) -> Document:
        if documents_info := self._document_service.get_brief_documents_info([document_id]):
            return documents_info[FIRST_ELEMENT]
        raise RuntimeError("Document with id %s doesn't exist." % document_id)
