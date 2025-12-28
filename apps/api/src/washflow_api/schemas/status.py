"""Status schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class StatusCreate(BaseModel):
    """Status creation schema."""

    name: str = Field(min_length=2, max_length=40)
    is_terminal: bool = Field(default=False)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class StatusUpdate(BaseModel):
    """Status update schema."""

    name: str | None = Field(default=None, min_length=2, max_length=40)
    is_terminal: bool | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        if v is not None:
            return v.strip()
        return v


class StatusOut(BaseModel):
    """Status response schema."""

    id: str
    organization_id: str
    location_id: str
    name: str
    sort_order: int
    is_terminal: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StatusListResponse(BaseModel):
    """Paginated status list response."""

    items: list[StatusOut]
    total: int


class StatusReorderRequest(BaseModel):
    """Request to reorder statuses."""

    ordered_ids: list[str] = Field(min_length=1)
