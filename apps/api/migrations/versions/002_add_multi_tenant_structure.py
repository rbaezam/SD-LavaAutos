"""Add multi-tenant structure (organizations, locations, update users)

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
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
    )
    op.create_index("ix_organizations_name", "organizations", ["name"])

    # Create locations table
    op.create_table(
        "locations",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
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
    op.create_index("ix_locations_organization_id", "locations", ["organization_id"])
    op.create_index(
        "ix_locations_org_name",
        "locations",
        ["organization_id", "name"],
        unique=True,
    )

    # Add new columns to users table
    # First add columns as nullable
    op.add_column(
        "users",
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("location_id", postgresql.UUID(as_uuid=False), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("role", sa.String(50), nullable=True),
    )

    # Data migration: create default org for existing users
    conn = op.get_bind()

    # Check if there are existing users
    result = conn.execute(sa.text("SELECT id FROM users LIMIT 1"))
    existing_users = result.fetchone()

    if existing_users:
        # Create a default organization
        default_org_id = str(uuid4())
        conn.execute(
            sa.text(
                "INSERT INTO organizations (id, name) VALUES (:id, :name)"
            ),
            {"id": default_org_id, "name": "Default Organization"},
        )

        # Update all existing users to belong to this org as owners
        conn.execute(
            sa.text(
                "UPDATE users SET organization_id = :org_id, role = 'owner'"
            ),
            {"org_id": default_org_id},
        )

    # Now make organization_id and role NOT NULL
    op.alter_column("users", "organization_id", nullable=False)
    op.alter_column("users", "role", nullable=False, server_default="staff")

    # Create foreign key constraints
    op.create_foreign_key(
        "fk_users_organization_id",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_users_location_id",
        "users",
        "locations",
        ["location_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create indexes
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_index("ix_users_location_id", "users", ["location_id"])
    op.create_index("ix_users_role", "users", ["role"])


def downgrade() -> None:
    # Remove indexes from users
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_location_id", table_name="users")
    op.drop_index("ix_users_organization_id", table_name="users")

    # Remove foreign keys
    op.drop_constraint("fk_users_location_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_organization_id", "users", type_="foreignkey")

    # Remove columns from users
    op.drop_column("users", "role")
    op.drop_column("users", "location_id")
    op.drop_column("users", "organization_id")

    # Drop locations table
    op.drop_index("ix_locations_org_name", table_name="locations")
    op.drop_index("ix_locations_organization_id", table_name="locations")
    op.drop_table("locations")

    # Drop organizations table
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.drop_table("organizations")
