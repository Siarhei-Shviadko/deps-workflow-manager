from typing import Any, Optional

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_workflow_manager.extras.settings import DatabaseSettings, ServiceInfoSettings


class FileStorageSettings(BaseSettings):
    url: Optional[str] = None
    external_url: Optional[str] = None

    model_config = SettingsConfigDict(env_prefix="file_storage_", case_sensitive=False)


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    documentation_enabled: bool = Field(default=True, validation_alias="DOCUMENTATION_ENABLED")

    info: ServiceInfoSettings = ServiceInfoSettings()
    database: DatabaseSettings = DatabaseSettings()

    verify_ssl: bool = Field(default=True, validation_alias="AUTH_VERIFY_SSL")

    messaging_driver: MessagingDriverEnum = Field(
        default=MessagingDriverEnum.RABBITMQ,
        validation_alias="MESSAGING_DRIVER",
    )
    messaging_driver_settings: Any = Field(default=None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    file_storage: FileStorageSettings = FileStorageSettings()
    document_type_service_url: str
    template_service_url: str
    document_service_url: str
    extraction_service_url: str

    version_classification_enabled: bool = False
    classification_enabled: bool = False
    exceptional_queue_enabled: bool = False
    validation_enabled: bool = False

    instrumentation_enabled: bool = False

    model_config = SettingsConfigDict(use_enum_values=True)

    @classmethod
    @field_validator("messaging_driver_settings")
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
