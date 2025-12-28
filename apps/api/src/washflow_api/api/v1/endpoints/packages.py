"""Packages API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db.session import get_db
from washflow_api.schemas.package import (
    PackageCreate,
    PackageListResponse,
    PackageOut,
    PackageServiceOut,
    PackageSimple,
    PackageUpdate,
    ServiceSimple,
    VehicleTypeSimple,
)
from washflow_api.services.package import PackageServiceBiz

router = APIRouter()


def _build_package_out(package) -> PackageOut:
    """Build PackageOut from package model."""
    vehicle_type = None
    if package.vehicle_type:
        vehicle_type = VehicleTypeSimple(
            id=package.vehicle_type.id,
            name=package.vehicle_type.name,
        )

    services = []
    for ps in package.services:
        service_simple = None
        if ps.service:
            service_simple = ServiceSimple(
                id=ps.service.id,
                name=ps.service.name,
            )
        services.append(
            PackageServiceOut(
                id=ps.id,
                service_id=ps.service_id,
                sort_order=ps.sort_order,
                service=service_simple,
            )
        )

    return PackageOut(
        id=package.id,
        organization_id=package.organization_id,
        name=package.name,
        description=package.description,
        base_price_mxn=package.base_price_mxn,
        vehicle_type_id=package.vehicle_type_id,
        workers_required=package.workers_required,
        estimated_duration_minutes=package.estimated_duration_minutes,
        commission_per_worker_mxn=package.commission_per_worker_mxn,
        is_active=package.is_active,
        sort_order=package.sort_order,
        created_at=package.created_at,
        updated_at=package.updated_at,
        vehicle_type=vehicle_type,
        services=services,
    )


def _build_package_simple(package) -> PackageSimple:
    """Build PackageSimple from package model."""
    service_names = []
    for ps in package.services:
        if ps.service:
            service_names.append(ps.service.name)

    return PackageSimple(
        id=package.id,
        name=package.name,
        description=package.description,
        base_price_mxn=package.base_price_mxn,
        vehicle_type_id=package.vehicle_type_id,
        vehicle_type_name=package.vehicle_type.name if package.vehicle_type else None,
        workers_required=package.workers_required,
        estimated_duration_minutes=package.estimated_duration_minutes,
        service_names=service_names,
    )


@router.get("", response_model=PackageListResponse)
async def list_packages(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    vehicle_type_id: str | None = Query(default=None),
    include_inactive: bool = False,
) -> PackageListResponse:
    """List packages for the organization."""
    service = PackageServiceBiz(db)

    # Only managers can see inactive packages
    if include_inactive and current_user.role not in ("owner", "admin"):
        include_inactive = False

    packages = await service.list_packages(
        organization_id=current_user.organization_id,
        vehicle_type_id=vehicle_type_id,
        include_inactive=include_inactive,
    )

    return PackageListResponse(
        items=[_build_package_out(p) for p in packages],
        total=len(packages),
    )


@router.get("/simple", response_model=list[PackageSimple])
async def list_packages_simple(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    vehicle_type_id: str | None = Query(default=None),
) -> list[PackageSimple]:
    """List packages in simplified format for ticket creation."""
    service = PackageServiceBiz(db)

    packages = await service.list_packages(
        organization_id=current_user.organization_id,
        vehicle_type_id=vehicle_type_id,
        include_inactive=False,
    )

    return [_build_package_simple(p) for p in packages]


@router.post("", response_model=PackageOut, status_code=201)
async def create_package(
    data: PackageCreate,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PackageOut:
    """Create a new package."""
    service = PackageServiceBiz(db)

    try:
        package = await service.create_package(
            organization_id=current_user.organization_id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return _build_package_out(package)


@router.get("/{package_id}", response_model=PackageOut)
async def get_package(
    package_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PackageOut:
    """Get a package by ID."""
    service = PackageServiceBiz(db)

    package = await service.get_package(
        package_id=package_id,
        organization_id=current_user.organization_id,
    )

    if not package:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")

    return _build_package_out(package)


@router.patch("/{package_id}", response_model=PackageOut)
async def update_package(
    package_id: str,
    data: PackageUpdate,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PackageOut:
    """Update a package."""
    service = PackageServiceBiz(db)

    try:
        package = await service.update_package(
            package_id=package_id,
            organization_id=current_user.organization_id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return _build_package_out(package)


@router.delete("/{package_id}", status_code=204)
async def delete_package(
    package_id: str,
    current_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete (deactivate) a package."""
    service = PackageServiceBiz(db)

    deleted = await service.delete_package(
        package_id=package_id,
        organization_id=current_user.organization_id,
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Paquete no encontrado")
