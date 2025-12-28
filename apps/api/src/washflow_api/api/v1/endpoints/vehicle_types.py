"""Vehicle types API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db.session import get_db
from washflow_api.schemas.vehicle_type import (
    VehicleTypeCreate,
    VehicleTypeListResponse,
    VehicleTypeOut,
    VehicleTypeUpdate,
)
from washflow_api.services.vehicle_type import VehicleTypeService

router = APIRouter()


@router.get("", response_model=VehicleTypeListResponse)
async def list_vehicle_types(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_inactive: bool = False,
) -> VehicleTypeListResponse:
    """List vehicle types for the organization."""
    service = VehicleTypeService(db)

    # Only managers can see inactive vehicle types
    if include_inactive and not current_user.role in ("owner", "admin"):
        include_inactive = False

    vehicle_types = await service.list_vehicle_types(
        organization_id=current_user.organization_id,
        include_inactive=include_inactive,
    )

    return VehicleTypeListResponse(
        items=[VehicleTypeOut.model_validate(vt) for vt in vehicle_types],
        total=len(vehicle_types),
    )


@router.post("", response_model=VehicleTypeOut, status_code=201)
async def create_vehicle_type(
    data: VehicleTypeCreate,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VehicleTypeOut:
    """Create a new vehicle type."""
    service = VehicleTypeService(db)

    vehicle_type = await service.create_vehicle_type(
        organization_id=current_user.organization_id,
        data=data,
    )

    return VehicleTypeOut.model_validate(vehicle_type)


@router.get("/{vehicle_type_id}", response_model=VehicleTypeOut)
async def get_vehicle_type(
    vehicle_type_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VehicleTypeOut:
    """Get a vehicle type by ID."""
    service = VehicleTypeService(db)

    vehicle_type = await service.get_vehicle_type(
        vehicle_type_id=vehicle_type_id,
        organization_id=current_user.organization_id,
    )

    if not vehicle_type:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")

    return VehicleTypeOut.model_validate(vehicle_type)


@router.patch("/{vehicle_type_id}", response_model=VehicleTypeOut)
async def update_vehicle_type(
    vehicle_type_id: str,
    data: VehicleTypeUpdate,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> VehicleTypeOut:
    """Update a vehicle type."""
    service = VehicleTypeService(db)

    try:
        vehicle_type = await service.update_vehicle_type(
            vehicle_type_id=vehicle_type_id,
            organization_id=current_user.organization_id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return VehicleTypeOut.model_validate(vehicle_type)


@router.delete("/{vehicle_type_id}", status_code=204)
async def delete_vehicle_type(
    vehicle_type_id: str,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete (deactivate) a vehicle type."""
    service = VehicleTypeService(db)

    deleted = await service.delete_vehicle_type(
        vehicle_type_id=vehicle_type_id,
        organization_id=current_user.organization_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Tipo de vehículo no encontrado")
