"""Ticket endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db import get_db
from washflow_api.schemas.ticket import (
    EtaUpdateRequest,
    TicketCreate,
    TicketEventListResponse,
    TicketEventOut,
    TicketListItem,
    TicketListResponse,
    TicketMoveRequest,
    TicketOut,
    TicketUpdate,
)
from washflow_api.services.ticket import TicketServiceBiz

router = APIRouter()


def _validate_location_access(user, location_id: str) -> None:
    """Validate that user can access the specified location."""
    # Staff with assigned location can only access that location
    if user.is_staff and user.location_id:
        if user.location_id != location_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta sucursal",
            )


def _build_services_summary(ticket) -> str:
    """Build a summary string of service names."""
    if not ticket.services:
        return ""
    names = [s.captured_name for s in ticket.services[:3]]
    summary = ", ".join(names)
    if len(ticket.services) > 3:
        summary += f" +{len(ticket.services) - 3}"
    return summary


@router.post(
    "/locations/{location_id}/tickets",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    location_id: str,
    data: TicketCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketOut:
    """Create a new ticket in a location."""
    _validate_location_access(current_user, location_id)

    service = TicketServiceBiz(db)
    try:
        ticket = await service.create_ticket(
            data=data,
            location_id=location_id,
            organization_id=current_user.organization_id,
            actor=current_user,
        )
        return TicketOut.model_validate(ticket)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/locations/{location_id}/tickets", response_model=TicketListResponse)
async def list_tickets(
    location_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_id: str | None = Query(default=None, description="Filter by status"),
    q: str | None = Query(default=None, description="Search query"),
    date: str | None = Query(
        default=None, description="Date filter: 'today' or empty for all"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> TicketListResponse:
    """List tickets for a location with optional filters."""
    _validate_location_access(current_user, location_id)

    service = TicketServiceBiz(db)
    tickets, total = await service.list_tickets(
        location_id=location_id,
        organization_id=current_user.organization_id,
        status_id=status_id,
        search=q,
        date_filter=date,
        skip=skip,
        limit=limit,
    )

    items = []
    for ticket in tickets:
        items.append(
            TicketListItem(
                id=ticket.id,
                public_code=ticket.public_code,
                plate=ticket.plate,
                vehicle_desc=ticket.vehicle_desc,
                current_status_id=ticket.current_status_id,
                current_status=ticket.current_status,
                eta_at=ticket.eta_at,
                created_at=ticket.created_at,
                services_summary=_build_services_summary(ticket),
                total_duration_minutes=ticket.total_duration_minutes,
            )
        )

    return TicketListResponse(items=items, total=total)


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketOut:
    """Get a specific ticket by ID."""
    service = TicketServiceBiz(db)
    ticket = await service.get_ticket(
        ticket_id=ticket_id,
        organization_id=current_user.organization_id,
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

    # Validate location access for staff
    _validate_location_access(current_user, ticket.location_id)

    return TicketOut.model_validate(ticket)


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
async def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketOut:
    """Update a ticket's fields."""
    service = TicketServiceBiz(db)
    ticket = await service.get_ticket(
        ticket_id=ticket_id,
        organization_id=current_user.organization_id,
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

    _validate_location_access(current_user, ticket.location_id)

    try:
        updated_ticket = await service.update_ticket(
            ticket=ticket,
            data=data,
            actor=current_user,
        )
        return TicketOut.model_validate(updated_ticket)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/tickets/{ticket_id}/move", response_model=TicketOut)
async def move_ticket(
    ticket_id: str,
    data: TicketMoveRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketOut:
    """Move a ticket to a different status."""
    service = TicketServiceBiz(db)
    ticket = await service.get_ticket(
        ticket_id=ticket_id,
        organization_id=current_user.organization_id,
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

    _validate_location_access(current_user, ticket.location_id)

    try:
        updated_ticket = await service.move_ticket(
            ticket=ticket,
            to_status_id=data.to_status_id,
            actor=current_user,
        )
        return TicketOut.model_validate(updated_ticket)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/tickets/{ticket_id}/eta", response_model=TicketOut)
async def update_ticket_eta(
    ticket_id: str,
    data: EtaUpdateRequest,
    manager_user: ManagerUser,  # Only owner/admin can manually set ETA
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketOut:
    """Update a ticket's ETA manually (owner/admin only)."""
    service = TicketServiceBiz(db)
    ticket = await service.get_ticket(
        ticket_id=ticket_id,
        organization_id=manager_user.organization_id,
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

    updated_ticket = await service.update_eta(
        ticket=ticket,
        eta_at=data.eta_at,
        actor=manager_user,
    )
    return TicketOut.model_validate(updated_ticket)


@router.get("/tickets/{ticket_id}/events", response_model=TicketEventListResponse)
async def list_ticket_events(
    ticket_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TicketEventListResponse:
    """List all events for a ticket in chronological order."""
    service = TicketServiceBiz(db)

    # First check ticket exists and user has access
    ticket = await service.get_ticket(
        ticket_id=ticket_id,
        organization_id=current_user.organization_id,
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado",
        )

    _validate_location_access(current_user, ticket.location_id)

    events = await service.list_events(
        ticket_id=ticket_id,
        organization_id=current_user.organization_id,
    )

    items = []
    for event in events:
        items.append(
            TicketEventOut(
                id=event.id,
                ticket_id=event.ticket_id,
                actor_user_id=event.actor_user_id,
                actor_name=event.actor.full_name if event.actor else None,
                event_type=event.event_type,
                from_status_id=event.from_status_id,
                from_status_name=event.from_status.name if event.from_status else None,
                to_status_id=event.to_status_id,
                to_status_name=event.to_status.name if event.to_status else None,
                payload_json=event.payload_json,
                happened_at=event.happened_at,
            )
        )

    return TicketEventListResponse(items=items, total=len(items))
