"""Ticket model."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from washflow_api.db.base import Base

if TYPE_CHECKING:
    from washflow_api.models.location import Location
    from washflow_api.models.notification import NotificationLog
    from washflow_api.models.organization import Organization
    from washflow_api.models.package import Package
    from washflow_api.models.status import Status
    from washflow_api.models.ticket_event import TicketEvent
    from washflow_api.models.ticket_service import TicketService
    from washflow_api.models.vehicle_type import VehicleType


class Ticket(Base):
    """Ticket model for vehicle tracking."""

    __tablename__ = "tickets"

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
    location_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
    )
    public_code: Mapped[str] = mapped_column(String(16), nullable=False)
    plate: Mapped[str | None] = mapped_column(String(16), nullable=True)
    vehicle_desc: Mapped[str | None] = mapped_column(String(80), nullable=True)
    manual_ticket_no: Mapped[str | None] = mapped_column(String(24), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(60), nullable=True)
    customer_whatsapp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    current_status_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("statuses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    eta_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Package and vehicle type (optional for backwards compatibility)
    package_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("packages.id", ondelete="SET NULL"),
        nullable=True,
    )
    vehicle_type_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("vehicle_types.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Captured values from package at ticket creation (for historical accuracy)
    captured_package_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    captured_package_price_mxn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_workers_required: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_estimated_duration_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
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
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    location: Mapped["Location"] = relationship("Location", back_populates="tickets")
    current_status: Mapped["Status"] = relationship("Status", foreign_keys=[current_status_id])
    package: Mapped["Package | None"] = relationship("Package", lazy="joined")
    vehicle_type: Mapped["VehicleType | None"] = relationship("VehicleType", lazy="joined")
    services: Mapped[list["TicketService"]] = relationship(
        "TicketService",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketService.sort_order",
    )
    events: Mapped[list["TicketEvent"]] = relationship(
        "TicketEvent",
        back_populates="ticket",
        cascade="all, delete-orphan",
        order_by="TicketEvent.happened_at",
    )
    notification_logs: Mapped[list["NotificationLog"]] = relationship(
        "NotificationLog",
        back_populates="ticket",
        lazy="noload",
    )

    @property
    def total_duration_minutes(self) -> int:
        """Calculate total duration from all services."""
        return sum(s.captured_duration_minutes for s in self.services)

    @property
    def total_price_mxn(self) -> int | None:
        """Calculate total price from all services (None if any service has no price)."""
        prices = [s.captured_price_mxn for s in self.services if s.captured_price_mxn is not None]
        if not prices:
            return None
        return sum(prices)
