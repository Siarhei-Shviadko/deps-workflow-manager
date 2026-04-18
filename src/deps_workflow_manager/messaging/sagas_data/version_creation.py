import logging
from typing import Any, Optional

from deps_message_flow.commands.consumer import (
    CommandWithDestination,
    CommandWithDestinationBuilder,
)
from deps_message_flow.sagas.orchestration import SagaData

from ..commands import (
    CreateVersion,
    DeleteFiles,
    ImplementAutoMarkup,
    PreprocessReferencePage,
)

__all__ = ["VersionCreationSagaData"]


class VersionCreationSagaData(SagaData):  # noqa: WPS230
    def __init__(
        self,
        template_id: str,
        tenant_id: str,
        name: str,
        original_blob_names: list[str],
        preprocessed_blob_names: Optional[list[str]] = None,
        *,
        description: Optional[str] = None,
        markup_automatically: bool = False,
        version_id: Optional[str] = None,
        auto_markup_failed: bool = False,
    ) -> None:
        super().__init__(entity_id=template_id)
        self.tenant_id = tenant_id
        self.name = name
        self.original_blob_names = original_blob_names
        self.preprocessed_blob_names = preprocessed_blob_names
        self.description = description
        self.markup_automatically = markup_automatically
        self.version_id = version_id
        self.auto_markup_failed = auto_markup_failed

        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def template_id(self) -> str:
        return self.entity_id

    @template_id.setter
    def template_id(self, value: str) -> None:
        self.entity_id = value

    def should_implement_auto_markup(self) -> bool:
        return self.markup_automatically

    def should_delete_preprocessed_files(self) -> bool:
        return not self.auto_markup_failed

    def preprocess_reference_pages(self) -> CommandWithDestination:
        self._logger.info(f"Starting preprocessing reference page for template {self.template_id}")

        return (
            CommandWithDestinationBuilder.send(
                PreprocessReferencePage(template_id=self.template_id, blob_names=self.original_blob_names),
            )
            .to("ImagePreprocessCommands")
            .build()
        )

    def delete_preprocessed_files(self) -> CommandWithDestination:
        return (
            CommandWithDestinationBuilder.send(DeleteFiles(file_paths=self.preprocessed_blob_names))
            .to("FileStorageCommands")
            .build()
        )

    def create_version(self):
        return (
            CommandWithDestinationBuilder.send(
                CreateVersion(
                    template_id=self.template_id,
                    tenant_id=self.tenant_id,
                    name=self.name,
                    original_blob_names=self.original_blob_names,
                    preprocessed_blob_names=self.preprocessed_blob_names,
                    description=self.description,
                ),
            )
            .to("TemplateCommands")
            .build()
        )

    def implement_auto_markup(self):
        if self.version_id is not None:
            return (
                CommandWithDestinationBuilder.send(
                    ImplementAutoMarkup(
                        template_id=self.template_id,
                        version_id=self.version_id,
                        tenant_id=self.tenant_id,
                    ),
                )
                .to("TemplateCommands")
                .build()
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "original_blob_names": self.original_blob_names,
            "preprocessed_blob_names": self.preprocessed_blob_names,
            "description": self.description,
            "version_id": self.version_id,
            "markup_automatically": self.markup_automatically,
            "auto_markup_failed": self.auto_markup_failed,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "VersionCreationSagaData":
        return cls(
            template_id=raw_data["entity_id"],
            tenant_id=raw_data["tenant_id"],
            name=raw_data["name"],
            original_blob_names=raw_data["original_blob_names"],
            preprocessed_blob_names=raw_data["preprocessed_blob_names"],
            description=raw_data["description"],
            version_id=raw_data["version_id"],
            markup_automatically=raw_data["markup_automatically"],
            auto_markup_failed=raw_data["auto_markup_failed"],
        )
