"""Public endpoints (no authentication required)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.db import get_db
from washflow_api.schemas.ticket import PublicTicketOut
from washflow_api.services.ticket import TicketServiceBiz

router = APIRouter()


def _resolve_branding(
    location, organization
) -> tuple[str, str | None, str | None]:
    """Resolve branding with inheritance: location override > org > fallback.

    Returns (brand_name, brand_logo_url, brand_primary_color).
    """
    # Brand name: location override > org brand_name > org name > "WashFlow"
    brand_name = (
        location.brand_name_override
        or organization.brand_name
        or organization.name
        or "WashFlow"
    )

    # Logo URL: location override > org logo > None
    brand_logo_url = (
        location.brand_logo_url_override
        or organization.brand_logo_url
    )

    # Primary color: location override > org color > None
    brand_primary_color = (
        location.brand_primary_color_override
        or organization.brand_primary_color
    )

    return brand_name, brand_logo_url, brand_primary_color


@router.get("/tickets/{public_code}", response_model=PublicTicketOut)
async def get_public_ticket(
    public_code: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicTicketOut:
    """Get minimal ticket info by public code (no authentication required)."""
    # Normalize public code (uppercase, trim)
    normalized_code = public_code.strip().upper()

    service = TicketServiceBiz(db)
    ticket = await service.get_ticket_by_public_code(normalized_code)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

    # Build vehicle label (prefer plate, fallback to vehicle_desc)
    vehicle_label = ticket.plate or ticket.vehicle_desc or "Vehículo"

    # Build service name from ticket services
    service_name = None
    if ticket.services:
        service_names = [s.captured_name for s in ticket.services]
        service_name = ", ".join(service_names) if service_names else None

    # Resolve branding with inheritance
    brand_name, brand_logo_url, brand_primary_color = _resolve_branding(
        ticket.location, ticket.organization
    )

    return PublicTicketOut(
        public_code=ticket.public_code,
        vehicle_label=vehicle_label,
        service_name=service_name,
        status_name=ticket.current_status.name,
        status_is_terminal=ticket.current_status.is_terminal,
        eta_at=ticket.eta_at,
        updated_at=ticket.updated_at,
        location_name=ticket.location.name,
        organization_name=ticket.organization.name,
        brand_name=brand_name,
        brand_logo_url=brand_logo_url,
        brand_primary_color=brand_primary_color,
    )
