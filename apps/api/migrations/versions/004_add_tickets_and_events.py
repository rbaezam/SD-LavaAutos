"""Add tickets and events tables

Revision ID: 004
Revises: 003
Create Date: 2024-01-04 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tickets table
    op.create_table(
        "tickets",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("public_code", sa.String(16), nullable=False),
        sa.Column("plate", sa.String(16), nullable=True),
        sa.Column("vehicle_desc", sa.String(80), nullable=True),
        sa.Column("manual_ticket_no", sa.String(24), nullable=True),
        sa.Column("customer_name", sa.String(60), nullable=True),
        sa.Column("customer_whatsapp", sa.String(20), nullable=True),
        sa.Column("current_status_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("eta_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["current_status_id"],
            ["statuses.id"],
            ondelete="RESTRICT",
        ),
    )
    # Indexes for tickets
    op.create_index(
        "ix_tickets_org_location_created",
        "tickets",
        ["organization_id", "location_id", "created_at"],
    )
    op.create_index(
        "ix_tickets_location_status_created",
        "tickets",
        ["location_id", "current_status_id", "created_at"],
    )
    op.create_index(
        "ix_tickets_org_public_code",
        "tickets",
        ["organization_id", "public_code"],
        unique=True,
    )
    op.create_index("ix_tickets_plate", "tickets", ["plate"])
    op.create_index("ix_tickets_location_id", "tickets", ["location_id"])

    # Create ticket_services table (service snapshots)
    op.create_table(
        "ticket_services",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("captured_name", sa.String(60), nullable=False),
        sa.Column("captured_price_mxn", sa.Integer(), nullable=True),
        sa.Column("captured_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index("ix_ticket_services_ticket_id", "ticket_services", ["ticket_id"])

    # Create ticket_events table (audit log)
    op.create_table(
        "ticket_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_type", sa.String(24), nullable=False),
        sa.Column("from_status_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("to_status_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("payload_json", postgresql.JSONB(), nullable=True),
        sa.Column(
            "happened_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["from_status_id"],
            ["statuses.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["to_status_id"],
            ["statuses.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_ticket_events_ticket_happened",
        "ticket_events",
        ["ticket_id", "happened_at"],
    )


def downgrade() -> None:
    # Drop ticket_events table
    op.drop_index("ix_ticket_events_ticket_happened", table_name="ticket_events")
    op.drop_table("ticket_events")

    # Drop ticket_services table
    op.drop_index("ix_ticket_services_ticket_id", table_name="ticket_services")
    op.drop_table("ticket_services")

    # Drop tickets table
    op.drop_index("ix_tickets_location_id", table_name="tickets")
    op.drop_index("ix_tickets_plate", table_name="tickets")
    op.drop_index("ix_tickets_org_public_code", table_name="tickets")
    op.drop_index("ix_tickets_location_status_created", table_name="tickets")
    op.drop_index("ix_tickets_org_location_created", table_name="tickets")
    op.drop_table("tickets")
