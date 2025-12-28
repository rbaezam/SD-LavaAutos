"""Vehicle type schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VehicleTypeBase(BaseModel):
    """Base schema for vehicle type."""

    name: str = Field(..., min_length=1, max_length=60)
    description: str | None = None
    default_workers: int = Field(default=1, ge=1, le=10)
    default_duration_minutes: int = Field(default=30, ge=5, le=480)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0)


class VehicleTypeCreate(VehicleTypeBase):
    """Schema for creating a vehicle type."""

    pass


class VehicleTypeUpdate(BaseModel):
    """Schema for updating a vehicle type."""

    name: str | None = Field(default=None, min_length=1, max_length=60)
    description: str | None = None
    default_workers: int | None = Field(default=None, ge=1, le=10)
    default_duration_minutes: int | None = Field(default=None, ge=5, le=480)
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0)


class VehicleTypeOut(VehicleTypeBase):
    """Schema for vehicle type output."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime


class VehicleTypeListResponse(BaseModel):
    """Schema for vehicle type list response."""

    items: list[VehicleTypeOut]
    total: int
