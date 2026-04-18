from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_message_flow.sagas.orchestration import *
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_workflow_manager.application import (
    DocumentProcessingService,
    WorkflowConfigurationService,
    WorkflowService,
    WorkflowStateService,
)
from deps_workflow_manager.application.pipeline_service import PipelineService
from deps_workflow_manager.constants import PROJECT_NAME
from deps_workflow_manager.extras.datasource import Database, DBDialect, DBDriver
from deps_workflow_manager.extras.storage import StorageControllerService
from deps_workflow_manager.infrastructure.repositories import (
    DocumentProcessingInfoRepository,
    SagaInstanceRepository,
    WorkflowConfigurationRepository,
)
from deps_workflow_manager.infrastructure.services import (
    DocumentService,
    DocumentTypeService,
    ExtractionService,
    TemplateService,
)
from deps_workflow_manager.messaging.dispatcher import make_message_dispatcher
from deps_workflow_manager.messaging.sagas import *
from deps_workflow_manager.messaging.sagas.template_deletion import TemplateDeletionSaga
from deps_workflow_manager.messaging.sagas_data import *

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class DatabaseResource(resources.Resource):
    def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect,
        driver: DBDriver,
        require_secure_transport: bool,
        sslkey: str,
        sslcert: str,
        sslrootcert: str,
        sslmode: str,
    ) -> Database:
        db = Database(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            dialect=dialect,
            driver=driver,
            require_secure_transport=require_secure_transport,
            sslkey=sslkey,
            sslcert=sslcert,
            sslrootcert=sslrootcert,
            sslmode=sslmode,
        )
        db.connect()
        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        config.user,
        config.password,
        config.host,
        config.port,
        config.db,
        config.dialect,
        config.driver,
        config.require_secure_transport,
        sslkey=config.ssl.key,
        sslcert=config.ssl.cert,
        sslrootcert=config.ssl.rootcert,
        sslmode=config.ssl.mode,
    )


class Repositories(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()

    saga_instance: providers.Provider[SagaInstanceRepository] = providers.Singleton(
        SagaInstanceRepository,
        datasources.postgres_datasource,
    )
    workflow_configuration: providers.Provider[WorkflowConfigurationRepository] = providers.Singleton(
        WorkflowConfigurationRepository,
        datasources.postgres_datasource,
    )
    document_processing: providers.Provider[DocumentProcessingInfoRepository] = providers.Singleton(
        DocumentProcessingInfoRepository,
        datasources.postgres_datasource,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    document_type_service: providers.Singleton[DocumentTypeService] = providers.Singleton(
        DocumentTypeService,
        base_url=config.document_type_service_url,
    )
    document_service: providers.Singleton[DocumentService] = providers.Singleton(
        DocumentService,
        base_url=config.document_service_url,
    )
    template_service: providers.Singleton[TemplateService] = providers.Singleton(
        TemplateService,
        base_url=config.template_service_url,
    )
    extraction_service: providers.Singleton[ExtractionService] = providers.Singleton(
        ExtractionService,
        base_url=config.extraction_service_url,
    )


class SagaSteps(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    pipeline_service = providers.Dependency(instance_of=PipelineService)

    template_creation: providers.Singleton[TemplateCreationSteps] = providers.Singleton(
        TemplateCreationSteps,
        document_type_service=services.document_type_service,
        template_service=services.template_service,
        extraction_service=services.extraction_service,
    )
    template_create_from: providers.Singleton[TemplateCreateFromSteps] = providers.Singleton(
        TemplateCreateFromSteps,
        document_type_service=services.document_type_service,
        template_service=services.template_service,
        extraction_service=services.extraction_service,
    )
    complete_review: providers.Singleton[CompleteReviewSteps] = providers.Singleton(
        CompleteReviewSteps,
        document_service=services.document_service,
    )
    validate: providers.Singleton[ValidateSteps] = providers.Singleton(
        ValidateSteps,
        document_service=services.document_service,
    )
    template_deletion: providers.Singleton[TemplateDeletionSteps] = providers.Singleton(
        TemplateDeletionSteps,
        template_service=services.template_service,
        document_service=services.document_service,
    )
    plugin_processing: providers.Singleton[PluginProcessingSteps] = providers.Singleton(
        PluginProcessingSteps,
        document_service=services.document_service,
    )
    template_processing: providers.Singleton[TemplateProcessingSteps] = providers.Singleton(
        TemplateProcessingSteps,
        document_service=services.document_service,
    )
    full_processing: providers.Singleton[FullProcessingSteps] = providers.Singleton(
        FullProcessingSteps,
        workflow_configuration_repository=repositories.workflow_configuration,
    )
    document_processing: providers.Singleton[DocumentProcessingSteps] = providers.Singleton(
        DocumentProcessingSteps,
        workflow_configuration_repository=repositories.workflow_configuration,
        pipeline_service=pipeline_service,
    )
    typeless_processing: providers.Singleton[TypelessDocumentProcessingSteps] = providers.Singleton(
        TypelessDocumentProcessingSteps,
        pipeline_service=pipeline_service,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        datasources=datasources,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    storage_controller: providers.Singleton[StorageControllerService] = providers.Singleton(
        StorageControllerService,
        file_storage_url=config.file_storage.url,
    )
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )
    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    services: providers.Container[Services] = providers.Container(
        Services,
        config=config,
    )

    pipeline_service: providers.Singleton[PipelineService] = providers.Singleton(
        PipelineService,
        repositories.document_processing,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )
    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )
    saga_command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        SagaCommandProducer,
        command_producer,
    )
    saga_data_mapping: providers.Singleton[SagaDataMapping] = providers.Singleton(
        make_saga_data_mapping,
    )
    saga_manager_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaManagerFactory,
        repositories.saga_instance,
        command_producer,
        messaging.consumer,
        saga_command_producer,
        saga_data_mapping,
    )
    saga_steps: providers.Container[SagaSteps] = providers.Container(
        SagaSteps,
        services=services,
        repositories=repositories,
        pipeline_service=pipeline_service,
    )
    sagas = providers.List(
        providers.Singleton(
            PluginProcessingSaga,
            domain_event_publisher=domain_event_publisher,
            steps=saga_steps.plugin_processing,
        ),
        providers.Singleton(
            TemplateProcessingSaga,
            domain_event_publisher=domain_event_publisher,
            steps=saga_steps.template_processing,
        ),
        providers.Singleton(TemplateCreationSaga, steps=saga_steps.template_creation),
        providers.Singleton(TemplateCreateFromSaga, steps=saga_steps.template_create_from),
        providers.Singleton(VersionCreationSaga),
        providers.Singleton(
            CompleteReviewSaga,
            steps=saga_steps.complete_review,
            domain_event_publisher=domain_event_publisher,
        ),
        providers.Singleton(
            ValidateSaga,
            steps=saga_steps.validate,
            domain_event_publisher=domain_event_publisher,
        ),
        providers.Singleton(TemplateDeletionSaga, steps=saga_steps.template_deletion),
        providers.Singleton(FullProcessingSaga, steps=saga_steps.full_processing),
        providers.Singleton(DocumentsImportSaga),
        providers.Singleton(TypelessDocumentProcessingSaga, steps=saga_steps.typeless_processing),
        providers.Singleton(DocumentProcessingSaga, steps=saga_steps.document_processing),
    )
    saga_instance_factory: providers.Singleton[SagaManagerFactory] = providers.Singleton(
        SagaInstanceFactory,
        saga_manager_factory,
        sagas,
    )
    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )
    workflow_service: providers.Singleton[WorkflowService] = providers.Singleton(
        WorkflowService,
        storage_controller,
        services.document_service,
        sagas,
        saga_instance_factory,
        config.validation_enabled,
    )

    document_processing_service: providers.Singleton[DocumentProcessingService] = providers.Singleton(
        DocumentProcessingService,
        storage_proxy=storage_controller,
        document_service=services.document_service,
        sagas=sagas,
        saga_instance_factory=saga_instance_factory,
        version_classification_enabled=config.version_classification_enabled,
        classification_enabled=config.classification_enabled,
        exceptional_queue_enabled=config.exceptional_queue_enabled,
        document_processing_repository=repositories.document_processing,
    )

    workflow_state_service: providers.Singleton[WorkflowStateService] = providers.Singleton(
        WorkflowStateService,
        repositories.saga_instance,
        saga_data_mapping,
    )

    workflow_configuration_service: providers.Singleton[WorkflowConfigurationService] = providers.Singleton(
        WorkflowConfigurationService,
        repositories.workflow_configuration,
        command_producer,
    )
