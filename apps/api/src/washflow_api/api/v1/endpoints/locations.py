"""Location endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db import get_db
from washflow_api.schemas.location import (
    LocationCreate,
    LocationListResponse,
    LocationOut,
    LocationUpdate,
)
from washflow_api.services.location import LocationService

router = APIRouter()


@router.get("", response_model=LocationListResponse)
async def list_locations(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_inactive: bool = False,
) -> LocationListResponse:
    """List all locations for the current user's organization."""
    service = LocationService(db)
    locations, total = await service.list_locations(
        organization_id=current_user.organization_id,
        include_inactive=include_inactive,
    )
    return LocationListResponse(
        items=[LocationOut.model_validate(loc) for loc in locations],
        total=total,
    )


@router.get("/{location_id}", response_model=LocationOut)
async def get_location(
    location_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationOut:
    """Get a specific location."""
    service = LocationService(db)
    location = await service.get_location(
        location_id=location_id,
        organization_id=current_user.organization_id,
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )
    return LocationOut.model_validate(location)


@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationOut:
    """Create a new location (owner/admin only)."""
    service = LocationService(db)
    location = await service.create_location(
        data=data,
        organization_id=manager_user.organization_id,
    )
    return LocationOut.model_validate(location)


@router.patch("/{location_id}", response_model=LocationOut)
async def update_location(
    location_id: str,
    data: LocationUpdate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationOut:
    """Update a location (owner/admin only)."""
    service = LocationService(db)
    location = await service.get_location(
        location_id=location_id,
        organization_id=manager_user.organization_id,
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    location = await service.update_location(location, data)
    return LocationOut.model_validate(location)


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: str,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a location (owner/admin only)."""
    service = LocationService(db)
    location = await service.get_location(
        location_id=location_id,
        organization_id=manager_user.organization_id,
    )
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    await service.delete_location(location)
