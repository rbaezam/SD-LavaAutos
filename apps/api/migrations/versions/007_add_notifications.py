"""Add notification tables.

Revision ID: 007
Revises: 006
Create Date: 2024-12-28
"""

from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, tuple[str, ...], None] = None
depends_on: Union[str, tuple[str, ...], None] = None


def upgrade() -> None:
    # Create notification_provider_configs table
    op.create_table(
        "notification_provider_configs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False, server_default="mock"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config_json", postgresql.JSONB(), nullable=True),
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
        "ix_notification_provider_configs_org_channel",
        "notification_provider_configs",
        ["organization_id", "channel"],
        unique=True,
    )

    # Create notification_templates table
    op.create_table(
        "notification_templates",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("event", sa.String(30), nullable=False),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("message_template", sa.Text(), nullable=False),
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
    op.create_index(
        "ix_notification_templates_org_id",
        "notification_templates",
        ["organization_id"],
    )
    op.create_index(
        "ix_notification_templates_org_channel_event",
        "notification_templates",
        ["organization_id", "channel", "event"],
    )

    # Create notification_logs table
    op.create_table(
        "notification_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("channel", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("event", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("recipient", sa.String(50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(), nullable=True),
        sa.Column("response_json", postgresql.JSONB(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["tickets.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["notification_templates.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_notification_logs_ticket_id",
        "notification_logs",
        ["ticket_id"],
    )
    op.create_index(
        "ix_notification_logs_org_created",
        "notification_logs",
        ["organization_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_notification_logs_org_created", table_name="notification_logs")
    op.drop_index("ix_notification_logs_ticket_id", table_name="notification_logs")
    op.drop_table("notification_logs")

    op.drop_index(
        "ix_notification_templates_org_channel_event",
        table_name="notification_templates",
    )
    op.drop_index("ix_notification_templates_org_id", table_name="notification_templates")
    op.drop_table("notification_templates")

    op.drop_index(
        "ix_notification_provider_configs_org_channel",
        table_name="notification_provider_configs",
    )
    op.drop_table("notification_provider_configs")
