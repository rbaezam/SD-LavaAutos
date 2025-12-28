"""Add packages and vehicle types tables.

Revision ID: 008
Revises: 007
Create Date: 2024-12-28
"""

from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, tuple[str, ...], None] = None
depends_on: Union[str, tuple[str, ...], None] = None


def upgrade() -> None:
    # Create vehicle_types table
    op.create_table(
        "vehicle_types",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_workers", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "default_duration_minutes", sa.Integer(), nullable=False, server_default="30"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
    )
    op.create_index(
        "ix_vehicle_types_org_active",
        "vehicle_types",
        ["organization_id", "is_active"],
    )

    # Create packages table
    op.create_table(
        "packages",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("base_price_mxn", sa.Integer(), nullable=False),
        sa.Column("vehicle_type_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("workers_required", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "estimated_duration_minutes",
            sa.Integer(),
            nullable=False,
            server_default="30",
        ),
        sa.Column("commission_per_worker_mxn", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
            ["vehicle_type_id"],
            ["vehicle_types.id"],
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_packages_org_active",
        "packages",
        ["organization_id", "is_active"],
    )
    op.create_index(
        "ix_packages_vehicle_type",
        "packages",
        ["vehicle_type_id"],
    )

    # Create package_services pivot table
    op.create_table(
        "package_services",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("package_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["package_id"],
            ["packages.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_package_services_package",
        "package_services",
        ["package_id"],
    )

    # Add package-related columns to tickets table
    op.add_column(
        "tickets",
        sa.Column("package_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("vehicle_type_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("captured_package_name", sa.String(80), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("captured_package_price_mxn", sa.Integer(), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("captured_workers_required", sa.Integer(), nullable=True),
    )
    op.add_column(
        "tickets",
        sa.Column("captured_estimated_duration_minutes", sa.Integer(), nullable=True),
    )

    # Add foreign keys for package and vehicle_type on tickets
    op.create_foreign_key(
        "fk_tickets_package_id",
        "tickets",
        "packages",
        ["package_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_tickets_vehicle_type_id",
        "tickets",
        "vehicle_types",
        ["vehicle_type_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create indexes for the new ticket columns
    op.create_index("ix_tickets_package_id", "tickets", ["package_id"])
    op.create_index("ix_tickets_vehicle_type_id", "tickets", ["vehicle_type_id"])


def downgrade() -> None:
    # Remove indexes from tickets
    op.drop_index("ix_tickets_vehicle_type_id", table_name="tickets")
    op.drop_index("ix_tickets_package_id", table_name="tickets")

    # Remove foreign keys from tickets
    op.drop_constraint("fk_tickets_vehicle_type_id", "tickets", type_="foreignkey")
    op.drop_constraint("fk_tickets_package_id", "tickets", type_="foreignkey")

    # Remove columns from tickets
    op.drop_column("tickets", "captured_estimated_duration_minutes")
    op.drop_column("tickets", "captured_workers_required")
    op.drop_column("tickets", "captured_package_price_mxn")
    op.drop_column("tickets", "captured_package_name")
    op.drop_column("tickets", "vehicle_type_id")
    op.drop_column("tickets", "package_id")

    # Drop package_services table
    op.drop_index("ix_package_services_package", table_name="package_services")
    op.drop_table("package_services")

    # Drop packages table
    op.drop_index("ix_packages_vehicle_type", table_name="packages")
    op.drop_index("ix_packages_org_active", table_name="packages")
    op.drop_table("packages")

    # Drop vehicle_types table
    op.drop_index("ix_vehicle_types_org_active", table_name="vehicle_types")
    op.drop_table("vehicle_types")
