"""Service schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ServiceCreate(BaseModel):
    """Service creation schema."""

    name: str = Field(min_length=2, max_length=60)
    price_mxn: int | None = Field(default=None, ge=0)
    duration_minutes: int = Field(default=20, ge=1, le=600)
    sort_order: int = Field(default=0, ge=0)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class ServiceUpdate(BaseModel):
    """Service update schema."""

    name: str | None = Field(default=None, min_length=2, max_length=60)
    price_mxn: int | None = Field(default=None, ge=0)
    duration_minutes: int | None = Field(default=None, ge=1, le=600)
    sort_order: int | None = Field(default=None, ge=0)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip()
        return v


class ServiceOut(BaseModel):
    """Service response schema."""

    id: str
    organization_id: str
    location_id: str
    name: str
    active: bool
    price_mxn: int | None
    duration_minutes: int
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceListResponse(BaseModel):
    """Paginated service list response."""

    items: list[ServiceOut]
    total: int
