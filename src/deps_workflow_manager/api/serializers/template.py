from typing import Optional

from pydantic import Field

from .configured_base_serializer import ConfiguredBaseSerializer

__all__ = [
    "CreateTemplateRequest",
    "CreateTemplateResponse",
    "CreateTemplateFromRequest",
]


class CreateTemplateRequest(ConfiguredBaseSerializer):
    name: str
    language: str
    engine: str
    description: Optional[str] = Field(None, max_length=100)
    group_id: Optional[str] = Field(None, alias="groupId")


class CreateTemplateFromRequest(ConfiguredBaseSerializer):
    src_template_id: str = Field(alias="copyFrom")
    group_id: Optional[str] = Field(None, alias="groupId")
    description: Optional[str] = Field(None, max_length=100)
    name: str
    language: str
    engine: str


class CreateTemplateResponse(ConfiguredBaseSerializer):
    template_id: str = Field(alias="templateId")
