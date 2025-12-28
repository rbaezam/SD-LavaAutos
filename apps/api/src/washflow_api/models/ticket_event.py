"""TicketEvent model - audit log for ticket changes."""

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from washflow_api.db.base import Base

if TYPE_CHECKING:
    from washflow_api.models.status import Status
    from washflow_api.models.ticket import Ticket
    from washflow_api.models.user import User


class EventType(str, Enum):
    """Types of ticket events."""

    CREATED = "created"
    MOVED = "moved"
    EDITED = "edited"
    ETA_CHANGED = "eta_changed"


class TicketEvent(Base):
    """Audit log entry for ticket changes."""

    __tablename__ = "ticket_events"

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
    actor_user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(24), nullable=False)
    from_status_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("statuses.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_status_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("statuses.id", ondelete="SET NULL"),
        nullable=True,
    )
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    happened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # Relationships
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="events")
    actor: Mapped["User"] = relationship("User")
    from_status: Mapped["Status | None"] = relationship(
        "Status",
        foreign_keys=[from_status_id],
    )
    to_status: Mapped["Status | None"] = relationship(
        "Status",
        foreign_keys=[to_status_id],
    )
