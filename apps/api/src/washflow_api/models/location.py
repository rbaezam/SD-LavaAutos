"""Location model."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from washflow_api.db.base import Base

if TYPE_CHECKING:
    from washflow_api.models.organization import Organization
    from washflow_api.models.service import Service
    from washflow_api.models.status import Status
    from washflow_api.models.ticket import Ticket
    from washflow_api.models.user import User


class Location(Base):
    """Location (sucursal) model."""

    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Branding overrides (inherit from organization if null)
    brand_name_override: Mapped[str | None] = mapped_column(String(100), nullable=True)
    brand_logo_url_override: Mapped[str | None] = mapped_column(String(500), nullable=True)
    brand_primary_color_override: Mapped[str | None] = mapped_column(String(7), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="locations",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="location",
        lazy="selectin",
    )
    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="location",
        lazy="selectin",
    )
    statuses: Mapped[list["Status"]] = relationship(
        "Status",
        back_populates="location",
        lazy="selectin",
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="location",
        lazy="noload",
    )
