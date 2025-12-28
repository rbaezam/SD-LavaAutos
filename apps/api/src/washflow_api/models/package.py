"""Package model."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from washflow_api.db.base import Base


class Package(Base):
    """Represents a service package that customers can purchase."""

    __tablename__ = "packages"

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

    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    base_price_mxn: Mapped[int] = mapped_column(Integer, nullable=False)

    # Vehicle type association
    vehicle_type_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("vehicle_types.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Operational configuration
    workers_required: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
    commission_per_worker_mxn: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    organization = relationship("Organization")
    vehicle_type: Mapped["VehicleType"] = relationship(  # noqa: F821
        "VehicleType", back_populates="packages"
    )
    services: Mapped[list["PackageService"]] = relationship(
        "PackageService",
        back_populates="package",
        cascade="all, delete-orphan",
        order_by="PackageService.sort_order",
    )


class PackageService(Base):
    """Association between packages and services (pivot table)."""

    __tablename__ = "package_services"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    package_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("packages.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    package: Mapped["Package"] = relationship("Package", back_populates="services")
    service: Mapped["Service"] = relationship("Service")  # noqa: F821
