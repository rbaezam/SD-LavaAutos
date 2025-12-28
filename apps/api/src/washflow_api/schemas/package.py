"""Package schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServiceSimple(BaseModel):
    """Simplified service for package output."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class PackageServiceOut(BaseModel):
    """Schema for package service output."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    service_id: str
    sort_order: int
    service: ServiceSimple | None = None


class VehicleTypeSimple(BaseModel):
    """Simplified vehicle type for package output."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str


class PackageBase(BaseModel):
    """Base schema for package."""

    name: str = Field(..., min_length=1, max_length=80)
    description: str | None = None
    base_price_mxn: int = Field(..., ge=0)
    vehicle_type_id: str
    workers_required: int = Field(default=1, ge=1, le=10)
    estimated_duration_minutes: int = Field(default=30, ge=5, le=480)
    commission_per_worker_mxn: int | None = Field(default=None, ge=0)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)


class PackageCreate(PackageBase):
    """Schema for creating a package."""

    service_ids: list[str] = Field(default_factory=list)


class PackageUpdate(BaseModel):
    """Schema for updating a package."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = None
    base_price_mxn: int | None = Field(default=None, ge=0)
    vehicle_type_id: str | None = None
    workers_required: int | None = Field(default=None, ge=1, le=10)
    estimated_duration_minutes: int | None = Field(default=None, ge=5, le=480)
    commission_per_worker_mxn: int | None = Field(default=None, ge=0)
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)
    service_ids: list[str] | None = None


class PackageOut(PackageBase):
    """Schema for package output."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    # Related data
    vehicle_type: VehicleTypeSimple | None = None
    services: list[PackageServiceOut] = Field(default_factory=list)


class PackageListResponse(BaseModel):
    """Schema for package list response."""

    items: list[PackageOut]
    total: int


class PackageSimple(BaseModel):
    """Simplified package for ticket selection."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str | None = None
    base_price_mxn: int
    vehicle_type_id: str
    vehicle_type_name: str | None = None
    workers_required: int
    estimated_duration_minutes: int
    service_names: list[str] = Field(default_factory=list)
