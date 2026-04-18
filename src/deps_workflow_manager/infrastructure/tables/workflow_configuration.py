from sqlalchemy import Boolean, Column, String, Table
from sqlalchemy.dialects.postgresql import JSONB

from deps_workflow_manager.extras.datasource import metadata

__all__ = ["workflow_configuration_table"]


workflow_configuration_table = Table(
    "workflow_configuration",
    metadata,
    Column("tenant_id", String, primary_key=True),
    Column("document_type_id", String, primary_key=True),
    Column("extraction_type", String, nullable=True),
    Column("image_transformations", JSONB, nullable=True),
    Column("llm_type", String, nullable=True),
    Column("parsing_features", JSONB, nullable=True),
    Column("needs_extraction", Boolean, nullable=False),
    Column("needs_postprocessing", Boolean, nullable=False),
    Column("needs_validation", Boolean, nullable=False),
    Column("needs_user_verification", Boolean, nullable=False),
    Column("needs_output_exporting", Boolean, nullable=False),
    Column("needs_review_on_validation_failure", Boolean, nullable=False),
    Column("engine", String, nullable=True),
)
