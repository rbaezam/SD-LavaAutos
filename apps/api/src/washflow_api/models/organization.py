"""Organization model."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from washflow_api.db.base import Base

if TYPE_CHECKING:
    from washflow_api.models.location import Location
    from washflow_api.models.notification import NotificationProviderConfig, NotificationTemplate
    from washflow_api.models.user import User


class Organization(Base):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Branding fields
    brand_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    brand_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    brand_primary_color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Onboarding fields
    onboarding_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    onboarding_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
        lazy="selectin",
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location",
        back_populates="organization",
        lazy="selectin",
    )
    notification_provider_configs: Mapped[list["NotificationProviderConfig"]] = relationship(
        "NotificationProviderConfig",
        back_populates="organization",
        lazy="noload",
    )
    notification_templates: Mapped[list["NotificationTemplate"]] = relationship(
        "NotificationTemplate",
        back_populates="organization",
        lazy="noload",
    )
