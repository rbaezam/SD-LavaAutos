"""Add branding fields to organizations and locations

Revision ID: 005
Revises: 004
Create Date: 2024-01-05 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add branding columns to organizations
    op.add_column(
        "organizations",
        sa.Column("brand_name", sa.String(100), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("brand_logo_url", sa.String(500), nullable=True),
    )
    op.add_column(
        "organizations",
        sa.Column("brand_primary_color", sa.String(7), nullable=True),
    )

    # Add branding override columns to locations
    op.add_column(
        "locations",
        sa.Column("brand_name_override", sa.String(100), nullable=True),
    )
    op.add_column(
        "locations",
        sa.Column("brand_logo_url_override", sa.String(500), nullable=True),
    )
    op.add_column(
        "locations",
        sa.Column("brand_primary_color_override", sa.String(7), nullable=True),
    )


def downgrade() -> None:
    # Remove branding columns from locations
    op.drop_column("locations", "brand_primary_color_override")
    op.drop_column("locations", "brand_logo_url_override")
    op.drop_column("locations", "brand_name_override")

    # Remove branding columns from organizations
    op.drop_column("organizations", "brand_primary_color")
    op.drop_column("organizations", "brand_logo_url")
    op.drop_column("organizations", "brand_name")
