from typing import Any, Optional

from deps_message_flow.sagas.orchestration import SagaData

__all__ = ["TemplateCreationSagaData", "TemplateCreateFromSagaData"]


class TemplateCreationSagaData(SagaData):
    def __init__(
        self,
        name: str,
        language: str,
        engine: str,
        tenant_id: str,
        *,
        description: Optional[str] = None,
        template_id: Optional[str] = None,
        group_id: Optional[str] = None,
        original_exc: Optional[Exception] = None,
    ) -> None:
        super().__init__(entity_id=template_id)
        self.name = name
        self.language = language
        self.engine = engine
        self.tenant_id = tenant_id
        self.group_id = group_id
        self.description = description
        self._original_exc = original_exc

    @property
    def template_id(self) -> Optional[str]:
        return self.entity_id

    @template_id.setter
    def template_id(self, value: Optional[str]) -> None:
        self.entity_id = value

    @property
    def original_exc(self) -> Optional[Exception]:
        return self._original_exc

    @original_exc.setter
    def original_exc(self, exception: Exception) -> None:
        self._original_exc = exception

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "language": self.language,
            "engine": self.engine,
            "tenant_id": self.tenant_id,
            "entity_id": self.entity_id,
            "group_id": self.group_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "TemplateCreationSagaData":
        return cls(
            name=raw_data["name"],
            language=raw_data["language"],
            engine=raw_data["engine"],
            tenant_id=raw_data["tenant_id"],
            template_id=raw_data.get("entity_id"),
            group_id=raw_data.get("group_id"),
            description=raw_data.get("description"),
        )


class TemplateCreateFromSagaData(SagaData):
    def __init__(
        self,
        src_template_id: str,
        name: str,
        language: str,
        engine: str,
        tenant_id: str,
        *,
        description: Optional[str] = None,
        template_id: Optional[str] = None,
        group_id: Optional[str] = None,
        original_exc: Optional[Exception] = None,
    ) -> None:
        super().__init__(entity_id=template_id)
        self.src_template_id = src_template_id
        self.name = name
        self.language = language
        self.engine = engine
        self.tenant_id = tenant_id
        self.group_id = group_id
        self.description = description
        self._original_exc = original_exc

    @property
    def template_id(self) -> Optional[str]:
        return self.entity_id

    @template_id.setter
    def template_id(self, value: Optional[str]) -> None:
        self.entity_id = value

    @property
    def original_exc(self) -> Optional[Exception]:
        return self._original_exc

    @original_exc.setter
    def original_exc(self, exception: Exception) -> None:
        self._original_exc = exception

    def to_dict(self) -> dict[str, Any]:
        return {
            "src_template_id": self.src_template_id,
            "name": self.name,
            "language": self.language,
            "engine": self.engine,
            "tenant_id": self.tenant_id,
            "entity_id": self.entity_id,
            "group_id": self.group_id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "TemplateCreateFromSagaData":
        return cls(
            src_template_id=raw_data["src_template_id"],
            name=raw_data["name"],
            language=raw_data["language"],
            engine=raw_data["engine"],
            tenant_id=raw_data["tenant_id"],
            template_id=raw_data["entity_id"],
            group_id=raw_data.get("group_id"),
            description=raw_data.get("description"),
        )
