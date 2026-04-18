import logging
from typing import Any, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from deps_workflow_manager.constants import (
    COMMANDS_CHANNEL,
    DOCUMENT_IMPORT_SERVICE_CHANNEL,
)
from deps_workflow_manager.domain.constants import ImportSource
from deps_workflow_manager.domain.model import ParsingFeature

from ...commands import ImportDocuments, ProcessDocuments

__all__ = ["DocumentsImportSagaData"]

StringPair = tuple[str, str]


class DocumentsImportSagaData(SagaData):  # noqa: WPS230
    def __init__(
        self,
        paths: list[str],
        source: ImportSource,
        tenant_id: str,
        *,
        document_type_id: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        invoke_unifier: bool = False,
        invoke_extraction: bool = False,
        assign_to_me: bool = False,
        documents: Optional[list[StringPair]] = None,
        parsing_features: Optional[set[ParsingFeature]] = None,
    ) -> None:
        super().__init__(entity_id=None)
        self.paths = paths
        self.source = source
        self.document_type_id = document_type_id
        self.tenant_id = tenant_id
        self.engine = engine
        self.language = language
        self.llm_type = llm_type
        self.invoke_unifier = invoke_unifier
        self.invoke_extraction = invoke_extraction
        self.assign_to_me = assign_to_me
        self.documents = documents
        self.parsing_features = parsing_features

        self._logger = logging.getLogger(self.__class__.__name__)

    def import_documents(self) -> CommandWithDestination:
        self._logger.info(f"Importing documents from {self.source.value}")
        return (
            CommandWithDestinationBuilder.send(
                ImportDocuments(paths=self.paths, source=self.source.value),
            )
            .to(DOCUMENT_IMPORT_SERVICE_CHANNEL)
            .build()
        )

    def process_documents(self) -> CommandWithDestination:
        self._logger.info("Starting processing imported documents")
        return (
            CommandWithDestinationBuilder.send(
                ProcessDocuments(
                    documents=self.documents,
                    tenant_id=self.tenant_id,
                    document_type_id=self.document_type_id,
                    engine=self.engine,
                    language=self.language,
                    llm_type=self.llm_type,
                    invoke_unifier=self.invoke_unifier,
                    invoke_extraction=self.invoke_extraction,
                    assign_to_me=self.assign_to_me,
                    parsing_features=list(self.parsing_features) if self.parsing_features else None,
                ),
            )
            .to(COMMANDS_CHANNEL)
            .build()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "paths": self.paths,
            "source": self.source.value,
            "document_type_id": self.document_type_id,
            "tenant_id": self.tenant_id,
            "engine": self.engine,
            "language": self.language,
            "llm_type": self.llm_type,
            "invoke_unifier": self.invoke_unifier,
            "invoke_extraction": self.invoke_extraction,
            "assign_to_me": self.assign_to_me,
            "documents": self.documents,
            "parsing_features": list(self.parsing_features) if self.parsing_features else None,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "DocumentsImportSagaData":
        return cls(
            paths=raw_data["paths"],
            source=ImportSource(raw_data["source"]),
            document_type_id=raw_data["document_type_id"],
            tenant_id=raw_data["tenant_id"],
            engine=raw_data["engine"],
            language=raw_data["language"],
            llm_type=raw_data["llm_type"],
            invoke_unifier=raw_data["invoke_unifier"],
            invoke_extraction=raw_data["invoke_extraction"],
            assign_to_me=raw_data["assign_to_me"],
            documents=raw_data.get("documents"),
            parsing_features={ParsingFeature(feature) for feature in raw_data.get("parsing_features")}
            if raw_data.get("parsing_features")
            else None,
        )
