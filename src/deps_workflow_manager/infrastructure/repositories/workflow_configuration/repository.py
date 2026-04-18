from typing import Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert

from deps_workflow_manager.domain.model import (
    DocumentTypeInfo,
    IWorkflowConfigurationRepository,
    WorkflowConfiguration,
)
from deps_workflow_manager.extras.datasource import Database

from ...tables import workflow_configuration_table
from .mappers import DocumentTypeInfoMapper, WorkflowConfigurationMapper

__all__ = ["WorkflowConfigurationRepository"]


class WorkflowConfigurationRepository(IWorkflowConfigurationRepository):
    def __init__(self, database: Database):
        self.db = database

    def find(self, tenant_id: str, document_type_id: str) -> Optional[WorkflowConfiguration]:
        find_query = select(workflow_configuration_table).where(
            and_(
                workflow_configuration_table.c.tenant_id == tenant_id,
                workflow_configuration_table.c.document_type_id == document_type_id,
            ),
        )

        with self.db.connection() as connection:
            configuration_row = connection.execute(find_query).mappings().first()

        return WorkflowConfigurationMapper.from_dict(configuration_row) if configuration_row else None

    def find_all(self, tenant_id: str) -> list[WorkflowConfiguration]:
        find_query = select(workflow_configuration_table).where(
            workflow_configuration_table.c.tenant_id == tenant_id,
        )

        with self.db.connection() as connection:
            configuration_rows = connection.execute(find_query).mappings().all()
            return [WorkflowConfigurationMapper.from_dict(row) for row in configuration_rows]

    def save(self, configuration: WorkflowConfiguration) -> None:
        insert_query = insert(workflow_configuration_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=workflow_configuration_table.primary_key,
            set_=dict(insert_query.excluded),
        ).values(WorkflowConfigurationMapper.to_dict(configuration))

        with self.db.connection() as connection:
            connection.execute(save_query)

    def save_for(self, document_types: list[DocumentTypeInfo]) -> None:
        insert_query = insert(workflow_configuration_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=workflow_configuration_table.primary_key,
            set_={
                "extraction_type": insert_query.excluded.extraction_type,
                "image_transformations": insert_query.excluded.image_transformations,
                "llm_type": insert_query.excluded.llm_type,
                "engine": insert_query.excluded.engine,
            },
        )

        with self.db.connection() as connection:
            connection.execute(save_query, [DocumentTypeInfoMapper.to_dict(dt) for dt in document_types])

    def delete(self, tenant_id: str, document_type_id: str) -> None:
        delete_query = delete(workflow_configuration_table).where(
            and_(
                workflow_configuration_table.c.tenant_id == tenant_id,
                workflow_configuration_table.c.document_type_id == document_type_id,
            ),
        )

        with self.db.connection() as connection:
            connection.execute(delete_query)
