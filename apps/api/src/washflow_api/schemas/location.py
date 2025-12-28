"""Location schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    """Location creation schema."""

    name: str = Field(min_length=2, max_length=255)
    address: str | None = Field(default=None, max_length=500)


class LocationUpdate(BaseModel):
    """Location update schema."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    address: str | None = Field(default=None, max_length=500)


class LocationOut(BaseModel):
    """Location response schema."""

    id: str
    organization_id: str
    name: str
    address: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LocationListResponse(BaseModel):
    """Paginated location list response."""

    items: list[LocationOut]
    total: int
