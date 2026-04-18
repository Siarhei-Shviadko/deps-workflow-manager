from uuid import uuid4

from deps_message_flow.sagas.orchestration import ISagaInstanceRepository, SagaInstance
from sqlalchemy import join, select, update
from sqlalchemy.dialects.postgresql import Insert, insert

from deps_workflow_manager.domain.exceptions import NotFoundError
from deps_workflow_manager.extras.datasource import Database

from ...tables import entity_saga_pair_table, saga_table
from .mappers import build_entity_saga_pair_dict, build_saga_dict, build_saga_instance

__all__ = ["SagaInstanceRepository"]


class SagaInstanceRepository(ISagaInstanceRepository):
    def __init__(self, database: Database):
        self.db = database

    @property
    def save_entity_saga_pair_query(self) -> Insert:
        insert_entity_saga_pair_query = insert(entity_saga_pair_table)
        return insert_entity_saga_pair_query.on_conflict_do_update(
            constraint=entity_saga_pair_table.primary_key,
            set_=dict(insert_entity_saga_pair_query.excluded),
        )

    def save(self, saga_instance: SagaInstance) -> SagaInstance:
        saga_instance.saga_id = uuid4().hex
        insert_saga_query = insert(saga_table).values(build_saga_dict(saga_instance))

        entity_saga_pair_fields = build_entity_saga_pair_dict(saga_instance)

        with self.db.connection() as connection:
            connection.execute(insert_saga_query)

            if entity_saga_pair_fields["entity_id"]:
                connection.execute(self.save_entity_saga_pair_query.values(entity_saga_pair_fields))

        return saga_instance

    def find(self, saga_id: str) -> SagaInstance:
        query = select(saga_table).where(saga_table.c.saga_id == saga_id)

        with self.db.connection() as connection:
            saga_instance_row = connection.execute(query).mappings().first()

        if not saga_instance_row:
            raise NotFoundError(f"Saga instance with saga_id = {saga_id} not found.")

        return build_saga_instance(saga_instance_row)

    def find_for_entity(self, entity_id: str) -> SagaInstance:
        joined_tables = join(
            entity_saga_pair_table,
            saga_table,
            entity_saga_pair_table.c.saga_id == saga_table.c.saga_id,
        )
        query = select(saga_table).select_from(joined_tables).where(entity_saga_pair_table.c.entity_id == entity_id)

        with self.db.connection() as connection:
            saga_instance_row = connection.execute(query).mappings().first()

        if not saga_instance_row:
            raise NotFoundError(f"Saga instance for entity with id = {entity_id} not found.")

        return build_saga_instance(saga_instance_row)

    def update(self, saga_instance: SagaInstance) -> SagaInstance:
        fields_to_update = self._get_fields_to_update_from_saga_instance(saga_instance)

        query = update(saga_table).where(saga_table.c.saga_id == saga_instance.saga_id).values(**fields_to_update)

        entity_saga_pair_fields = build_entity_saga_pair_dict(saga_instance)

        with self.db.connection() as connection:
            connection.execute(query)

            if entity_saga_pair_fields["entity_id"]:
                connection.execute(self.save_entity_saga_pair_query.values(entity_saga_pair_fields))

        return saga_instance

    @staticmethod
    def _get_fields_to_update_from_saga_instance(saga_instance: SagaInstance) -> dict:
        fields_to_update = build_saga_dict(saga_instance)
        del fields_to_update["saga_id"]

        return fields_to_update
