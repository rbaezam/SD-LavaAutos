"""Ticket schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from washflow_api.schemas.status import StatusOut


class TicketServiceSnapshot(BaseModel):
    """Snapshot of a service attached to a ticket."""

    id: str
    service_id: str | None
    captured_name: str
    captured_price_mxn: int | None
    captured_duration_minutes: int
    sort_order: int

    model_config = {"from_attributes": True}


class TicketCreate(BaseModel):
    """Ticket creation schema."""

    plate: str | None = Field(default=None, max_length=16)
    vehicle_desc: str | None = Field(default=None, max_length=80)
    manual_ticket_no: str | None = Field(default=None, max_length=24)
    customer_name: str | None = Field(default=None, max_length=60)
    customer_whatsapp: str | None = Field(default=None, max_length=20)

    # Package-based creation (preferred)
    package_id: str | None = None
    vehicle_type_id: str | None = None

    # Legacy: manual service selection (for backwards compatibility)
    service_ids: list[str] = Field(default_factory=list)

    @field_validator("plate", "vehicle_desc", "manual_ticket_no", "customer_name")
    @classmethod
    def strip_string(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v

    @field_validator("customer_whatsapp")
    @classmethod
    def validate_whatsapp(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            # Basic validation: allow +52 prefix or 10 digits
            cleaned = v.replace(" ", "").replace("-", "")
            if not cleaned:
                return None
            # Accept +52... or just digits
            if cleaned.startswith("+"):
                if len(cleaned) < 10:
                    raise ValueError("Número de WhatsApp inválido")
            else:
                if not cleaned.isdigit():
                    raise ValueError("Número de WhatsApp debe contener solo dígitos")
                if len(cleaned) < 10:
                    raise ValueError("Número de WhatsApp inválido")
            return v
        return v


class TicketUpdate(BaseModel):
    """Ticket update schema."""

    plate: str | None = Field(default=None, max_length=16)
    vehicle_desc: str | None = Field(default=None, max_length=80)
    manual_ticket_no: str | None = Field(default=None, max_length=24)
    customer_name: str | None = Field(default=None, max_length=60)
    customer_whatsapp: str | None = Field(default=None, max_length=20)
    service_ids: list[str] | None = None

    @field_validator("plate", "vehicle_desc", "manual_ticket_no", "customer_name")
    @classmethod
    def strip_string(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            return v if v else None
        return v

    @field_validator("customer_whatsapp")
    @classmethod
    def validate_whatsapp(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            cleaned = v.replace(" ", "").replace("-", "")
            if not cleaned:
                return None
            if cleaned.startswith("+"):
                if len(cleaned) < 10:
                    raise ValueError("Número de WhatsApp inválido")
            else:
                if not cleaned.isdigit():
                    raise ValueError("Número de WhatsApp debe contener solo dígitos")
                if len(cleaned) < 10:
                    raise ValueError("Número de WhatsApp inválido")
            return v
        return v


class PackageSnapshot(BaseModel):
    """Snapshot of package info captured at ticket creation."""

    id: str | None
    name: str | None
    price_mxn: int | None
    workers_required: int | None
    estimated_duration_minutes: int | None
    vehicle_type_id: str | None
    vehicle_type_name: str | None

    model_config = {"from_attributes": True}


class TicketOut(BaseModel):
    """Ticket response schema."""

    id: str
    organization_id: str
    location_id: str
    public_code: str
    plate: str | None
    vehicle_desc: str | None
    manual_ticket_no: str | None
    customer_name: str | None
    customer_whatsapp: str | None
    current_status_id: str
    current_status: StatusOut
    eta_at: datetime | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    services: list[TicketServiceSnapshot]
    total_duration_minutes: int
    total_price_mxn: int | None

    # Package info
    package_id: str | None = None
    vehicle_type_id: str | None = None
    package_snapshot: PackageSnapshot | None = None

    model_config = {"from_attributes": True}


class TicketListItem(BaseModel):
    """Ticket list item schema (lighter than full TicketOut)."""

    id: str
    public_code: str
    plate: str | None
    vehicle_desc: str | None
    current_status_id: str
    current_status: StatusOut
    eta_at: datetime | None
    created_at: datetime
    services_summary: str  # e.g. "Lavado completo, Encerado"
    total_duration_minutes: int

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    """Paginated ticket list response."""

    items: list[TicketListItem]
    total: int


class TicketMoveRequest(BaseModel):
    """Request to move ticket to another status."""

    to_status_id: str


class EtaUpdateRequest(BaseModel):
    """Request to update ticket ETA."""

    eta_at: datetime | None


class TicketEventOut(BaseModel):
    """Ticket event response schema."""

    id: str
    ticket_id: str
    actor_user_id: str
    actor_name: str | None = None
    event_type: str
    from_status_id: str | None
    from_status_name: str | None = None
    to_status_id: str | None
    to_status_name: str | None = None
    payload_json: dict[str, Any] | None
    happened_at: datetime

    model_config = {"from_attributes": True}


class TicketEventListResponse(BaseModel):
    """List of ticket events."""

    items: list[TicketEventOut]
    total: int


class PublicTicketOut(BaseModel):
    """Public ticket response schema (minimal, non-sensitive data only)."""

    public_code: str
    vehicle_label: str  # plate or vehicle_desc, computed
    service_name: str | None  # e.g. "Lavado completo" or "Lavado completo, Encerado"
    status_name: str
    status_is_terminal: bool
    eta_at: datetime | None
    updated_at: datetime
    location_name: str
    organization_name: str

    # Branding fields (resolved with inheritance: location override > org > fallback)
    brand_name: str  # Display name for branding
    brand_logo_url: str | None  # URL to logo image
    brand_primary_color: str | None  # HEX color like #2563eb

    model_config = {"from_attributes": True}
