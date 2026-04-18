# flake8: noqa
from deps_message_flow.sagas.orchestration import SagaData, SagaDataMapping

from .complete_review import CompleteReviewSagaData
from .document_import import DocumentsImportSagaData
from .document_processing import DocumentProcessingSagaData
from .full_processing import FullProcessingSagaData
from .plugin import PluginProcessingSagaData
from .template import TemplateCreationSagaData, TemplateProcessingSagaData
from .typeless_document_processing import TypelessDocumentProcessingSagaData
from .validate import ValidateSagaData
from .version_creation import VersionCreationSagaData

__all__ = ["make_saga_data_mapping"]


def make_saga_data_mapping() -> SagaDataMapping:
    return SagaDataMapping(
        {
            SagaData.__name__: SagaData,
            PluginProcessingSagaData.__name__: PluginProcessingSagaData,
            TemplateCreationSagaData.__name__: TemplateCreationSagaData,
            VersionCreationSagaData.__name__: VersionCreationSagaData,
            TemplateProcessingSagaData.__name__: TemplateProcessingSagaData,
            CompleteReviewSagaData.__name__: CompleteReviewSagaData,
            ValidateSagaData.__name__: ValidateSagaData,
            FullProcessingSagaData.__name__: FullProcessingSagaData,
            DocumentsImportSagaData.__name__: DocumentsImportSagaData,
            TypelessDocumentProcessingSagaData.__name__: TypelessDocumentProcessingSagaData,
            DocumentProcessingSagaData.__name__: DocumentProcessingSagaData,
        }
    )
