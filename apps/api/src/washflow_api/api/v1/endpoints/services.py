"""Service catalog endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db import get_db
from washflow_api.schemas.service import (
    ServiceCreate,
    ServiceListResponse,
    ServiceOut,
    ServiceUpdate,
)
from washflow_api.services.location import LocationService
from washflow_api.services.service import ServiceCatalogService

router = APIRouter()


@router.get("/locations/{location_id}/services", response_model=ServiceListResponse)
async def list_services(
    location_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_inactive: bool = True,
) -> ServiceListResponse:
    """List all services for a location."""
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

    service = ServiceCatalogService(db)
    services, total = await service.list_services(
        location_id=location_id,
        organization_id=current_user.organization_id,
        include_inactive=include_inactive,
    )
    return ServiceListResponse(
        items=[ServiceOut.model_validate(s) for s in services],
        total=total,
    )


@router.post(
    "/locations/{location_id}/services",
    response_model=ServiceOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    location_id: str,
    data: ServiceCreate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ServiceOut:
    """Create a new service (owner/admin only)."""
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

    service = ServiceCatalogService(db)
    try:
        new_service = await service.create_service(
            data=data,
            location_id=location_id,
            organization_id=manager_user.organization_id,
        )
        return ServiceOut.model_validate(new_service)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.patch("/services/{service_id}", response_model=ServiceOut)
async def update_service(
    service_id: str,
    data: ServiceUpdate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ServiceOut:
    """Update a service (owner/admin only)."""
    service_catalog = ServiceCatalogService(db)
    service = await service_catalog.get_service(
        service_id=service_id,
        organization_id=manager_user.organization_id,
    )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )

    try:
        updated = await service_catalog.update_service(service, data)
        return ServiceOut.model_validate(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/services/{service_id}/activate", response_model=ServiceOut)
async def activate_service(
    service_id: str,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ServiceOut:
    """Activate a service (owner/admin only)."""
    service_catalog = ServiceCatalogService(db)
    service = await service_catalog.get_service(
        service_id=service_id,
        organization_id=manager_user.organization_id,
    )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )

    try:
        activated = await service_catalog.activate_service(service)
        return ServiceOut.model_validate(activated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/services/{service_id}/deactivate", response_model=ServiceOut)
async def deactivate_service(
    service_id: str,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ServiceOut:
    """Deactivate a service (owner/admin only)."""
    service_catalog = ServiceCatalogService(db)
    service = await service_catalog.get_service(
        service_id=service_id,
        organization_id=manager_user.organization_id,
    )
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )

    deactivated = await service_catalog.deactivate_service(service)
    return ServiceOut.model_validate(deactivated)
