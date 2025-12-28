"""Status endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db import get_db
from washflow_api.schemas.status import (
    StatusCreate,
    StatusListResponse,
    StatusOut,
    StatusReorderRequest,
    StatusUpdate,
)
from washflow_api.services.location import LocationService
from washflow_api.services.status import StatusService

router = APIRouter()


@router.get("/locations/{location_id}/statuses", response_model=StatusListResponse)
async def list_statuses(
    location_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StatusListResponse:
    """List all statuses for a location."""
    # Verify location belongs to user's org
    location_service = LocationService(db)
    location = await location_service.get_location(
        location_id=location_id,
        organization_id=current_user.organization_id,
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    service = StatusService(db)
    statuses, total = await service.list_statuses(
        location_id=location_id,
        organization_id=current_user.organization_id,
    )
    return StatusListResponse(
        items=[StatusOut.model_validate(s) for s in statuses],
        total=total,
    )


@router.post(
    "/locations/{location_id}/statuses",
    response_model=StatusOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_status(
    location_id: str,
    data: StatusCreate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StatusOut:
    """Create a new status (owner/admin only)."""
    # Verify location belongs to user's org
    location_service = LocationService(db)
    location = await location_service.get_location(
        location_id=location_id,
        organization_id=manager_user.organization_id,
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    service = StatusService(db)
    try:
        new_status = await service.create_status(
            data=data,
            location_id=location_id,
            organization_id=manager_user.organization_id,
        )
        return StatusOut.model_validate(new_status)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch("/statuses/{status_id}", response_model=StatusOut)
async def update_status(
    status_id: str,
    data: StatusUpdate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StatusOut:
    """Update a status (owner/admin only)."""
    service = StatusService(db)
    status_obj = await service.get_status(
        status_id=status_id,
        organization_id=manager_user.organization_id,
    )
    if not status_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado no encontrado",
        )

    try:
        updated = await service.update_status(status_obj, data)
        return StatusOut.model_validate(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/locations/{location_id}/statuses/reorder", response_model=StatusListResponse)
async def reorder_statuses(
    location_id: str,
    data: StatusReorderRequest,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StatusListResponse:
    """Reorder statuses for a location (owner/admin only)."""
    # Verify location belongs to user's org
    location_service = LocationService(db)
    location = await location_service.get_location(
        location_id=location_id,
        organization_id=manager_user.organization_id,
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    service = StatusService(db)
    try:
        statuses = await service.reorder_statuses(
            location_id=location_id,
            organization_id=manager_user.organization_id,
            ordered_ids=data.ordered_ids,
        )
        return StatusListResponse(
            items=[StatusOut.model_validate(s) for s in statuses],
            total=len(statuses),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
