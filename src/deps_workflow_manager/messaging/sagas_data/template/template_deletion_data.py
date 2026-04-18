from typing import Any

from deps_message_flow.sagas.orchestration import SagaData

__all__ = ["TemplateDeletionSagaData"]


class TemplateDeletionSagaData(SagaData):
    def __init__(
        self,
        tenant_id: str,
        template_id: str,
    ) -> None:
        super().__init__(entity_id=template_id)
        self.tenant_id = tenant_id

    @property
    def template_id(self) -> str:
        return self.entity_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "entity_id": self.entity_id,
        }

    @classmethod
    def from_dict(cls, raw_data: dict[str, Any]) -> "TemplateDeletionSagaData":
        return cls(
            tenant_id=raw_data["tenant_id"],
            template_id=raw_data["entity_id"],
        )
