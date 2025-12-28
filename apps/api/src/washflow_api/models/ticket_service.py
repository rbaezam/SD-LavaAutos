"""TicketService model - snapshot of service at ticket creation time."""

from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from washflow_api.db.base import Base

if TYPE_CHECKING:
    from washflow_api.models.service import Service
    from washflow_api.models.ticket import Ticket


class TicketService(Base):
    """Snapshot of a service when added to a ticket."""

    __tablename__ = "ticket_services"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    ticket_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
    )
    captured_name: Mapped[str] = mapped_column(String(60), nullable=False)
    captured_price_mxn: Mapped[int | None] = mapped_column(Integer, nullable=True)
    captured_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="services")
    service: Mapped["Service | None"] = relationship("Service")
