"""Add services and statuses tables

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create services table
    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("price_mxn", sa.Integer(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_services_location_id", "services", ["location_id"])
    op.create_index("ix_services_organization_id", "services", ["organization_id"])
    op.create_index(
        "ix_services_location_active_sort",
        "services",
        ["location_id", "active", "sort_order"],
    )
    # Unique constraint on active services name per location
    op.create_index(
        "ix_services_location_name_active",
        "services",
        ["location_id", "name"],
        unique=True,
        postgresql_where=sa.text("active = true"),
    )

    # Create statuses table
    op.create_table(
        "statuses",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(40), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_terminal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_statuses_location_id", "statuses", ["location_id"])
    op.create_index("ix_statuses_organization_id", "statuses", ["organization_id"])
    op.create_index(
        "ix_statuses_location_sort",
        "statuses",
        ["location_id", "sort_order"],
    )
    op.create_index(
        "ix_statuses_location_name",
        "statuses",
        ["location_id", "name"],
        unique=True,
    )


def downgrade() -> None:
    # Drop statuses table
    op.drop_index("ix_statuses_location_name", table_name="statuses")
    op.drop_index("ix_statuses_location_sort", table_name="statuses")
    op.drop_index("ix_statuses_organization_id", table_name="statuses")
    op.drop_index("ix_statuses_location_id", table_name="statuses")
    op.drop_table("statuses")

    # Drop services table
    op.drop_index("ix_services_location_name_active", table_name="services")
    op.drop_index("ix_services_location_active_sort", table_name="services")
    op.drop_index("ix_services_organization_id", table_name="services")
    op.drop_index("ix_services_location_id", table_name="services")
    op.drop_table("services")
