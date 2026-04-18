from sqlalchemy import Boolean, Column, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_workflow_manager.extras.datasource import metadata

__all__ = ["document_processing_info_table"]


document_processing_info_table = Table(
    "document_processing_info",
    metadata,
    Column("document_id", String(100), primary_key=True),
    Column("tenant_id", String(100), primary_key=True),
    Column("needs_unifier", Boolean, nullable=False),
    Column("needs_extraction", Boolean, nullable=False),
    Column("assign_to_me", Boolean, nullable=False),
    Column("parsing_features", JSONB, nullable=True),
)
