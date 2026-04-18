from typing import Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert

from deps_workflow_manager.domain.model import (
    DocumentProcessingInfo,
    IDocumentProcessingInfoRepository,
)
from deps_workflow_manager.extras.datasource import Database

from ...tables import document_processing_info_table
from .mapper import DocumentProcessingInfoMapper

__all__ = ["DocumentProcessingInfoRepository"]


class DocumentProcessingInfoRepository(IDocumentProcessingInfoRepository):
    def __init__(self, database: Database):
        self.db = database
        self._table = document_processing_info_table

    def find(self, document_id: str, tenant_id: str) -> Optional[DocumentProcessingInfo]:
        find_query = select(self._table).where(
            and_(
                self._table.c.tenant_id == tenant_id,
                self._table.c.document_id == document_id,
            ),
        )

        with self.db.connection() as connection:
            raw_data = connection.execute(find_query).mappings().first()

        return DocumentProcessingInfoMapper.from_dict(raw_data) if raw_data else None

    def save(self, info: DocumentProcessingInfo) -> None:
        insert_query = insert(self._table).values(DocumentProcessingInfoMapper.to_dict(info))
        insert_query = insert_query.on_conflict_do_nothing(index_elements=["document_id", "tenant_id"])

        with self.db.connection() as connection:
            connection.execute(insert_query)

    def delete(self, document_id: str, tenant_id: str) -> None:
        delete_query = delete(self._table).where(
            and_(
                self._table.c.tenant_id == tenant_id,
                self._table.c.document_id == document_id,
            ),
        )

        with self.db.connection() as connection:
            connection.execute(delete_query)
