"""Onboarding endpoints."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import ManagerUser
from washflow_api.db import get_db
from washflow_api.models import Location, Service, Status
from washflow_api.schemas.organization import OnboardingStatusOut, OnboardingStepUpdate

router = APIRouter()

# Default statuses preset (recommended flow)
DEFAULT_STATUSES_PRESET = [
    {"name": "En espera", "sort_order": 0, "is_terminal": False},
    {"name": "En lavado", "sort_order": 1, "is_terminal": False},
    {"name": "En secado", "sort_order": 2, "is_terminal": False},
    {"name": "Detallado", "sort_order": 3, "is_terminal": False},
    {"name": "Listo", "sort_order": 4, "is_terminal": False},
    {"name": "Entregado", "sort_order": 5, "is_terminal": True},
]

# Default services preset
DEFAULT_SERVICES_PRESET = [
    {"name": "Lavado exterior", "price_mxn": 80, "sort_order": 0},
    {"name": "Lavado completo", "price_mxn": 150, "sort_order": 1},
    {"name": "Aspirado", "price_mxn": 50, "sort_order": 2},
    {"name": "Encerado", "price_mxn": 100, "sort_order": 3},
    {"name": "Detallado", "price_mxn": 300, "sort_order": 4},
]


@router.get("", response_model=OnboardingStatusOut)
async def get_onboarding_status(
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OnboardingStatusOut:
    """Get current onboarding status with computed flags."""
    org = manager_user.organization
    org_id = manager_user.organization_id

    # Check if has locations
    location_count = await db.scalar(
        select(func.count(Location.id)).where(Location.organization_id == org_id)
    )
    has_location = (location_count or 0) > 0

    # Get first location for status/service check
    first_location = await db.scalar(
        select(Location.id).where(Location.organization_id == org_id).limit(1)
    )

    # Check if has statuses (for any location)
    has_statuses = False
    if first_location:
        status_count = await db.scalar(
            select(func.count(Status.id)).where(
                Status.organization_id == org_id,
                Status.location_id == first_location,
            )
        )
        has_statuses = (status_count or 0) > 0

    # Check if has services
    service_count = await db.scalar(
        select(func.count(Service.id)).where(Service.organization_id == org_id)
    )
    has_services = (service_count or 0) > 0

    # Check if has branding (either brand_name or brand_primary_color set)
    has_branding = bool(org.brand_name or org.brand_primary_color)

    return OnboardingStatusOut(
        onboarding_step=org.onboarding_step,
        onboarding_completed_at=org.onboarding_completed_at,
        has_location=has_location,
        has_statuses=has_statuses,
        has_services=has_services,
        has_branding=has_branding,
    )


@router.patch("", response_model=OnboardingStatusOut)
async def update_onboarding_step(
    data: OnboardingStepUpdate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OnboardingStatusOut:
    """Update onboarding step. Cannot go backwards if already completed."""
    org = manager_user.organization

    # Don't allow going backwards if already completed
    if org.onboarding_completed_at and data.onboarding_step < org.onboarding_step:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede retroceder en el onboarding una vez completado",
        )

    org.onboarding_step = data.onboarding_step
    await db.flush()
    await db.refresh(org)

    # Return full status
    return await get_onboarding_status(manager_user, db)


@router.post("/complete", response_model=OnboardingStatusOut)
async def complete_onboarding(
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OnboardingStatusOut:
    """Mark onboarding as complete."""
    org = manager_user.organization

    org.onboarding_step = 5
    org.onboarding_completed_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(org)

    return await get_onboarding_status(manager_user, db)


@router.post("/apply-status-preset", response_model=OnboardingStatusOut)
async def apply_status_preset(
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OnboardingStatusOut:
    """Apply recommended status preset. Idempotent - won't duplicate existing statuses."""
    org_id = manager_user.organization_id

    # Get first location (required for statuses)
    first_location = await db.scalar(
        select(Location.id).where(Location.organization_id == org_id).limit(1)
    )

    if not first_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primero debes crear una sucursal",
        )

    # Get existing status names for this location
    existing_statuses = await db.execute(
        select(Status.name).where(
            Status.organization_id == org_id,
            Status.location_id == first_location,
        )
    )
    existing_names = {name.lower() for (name,) in existing_statuses.all()}

    # Create missing statuses
    for status_data in DEFAULT_STATUSES_PRESET:
        if status_data["name"].lower() not in existing_names:
            new_status = Status(
                organization_id=org_id,
                location_id=first_location,
                name=status_data["name"],
                sort_order=status_data["sort_order"],
                is_terminal=status_data["is_terminal"],
            )
            db.add(new_status)

    await db.flush()

    return await get_onboarding_status(manager_user, db)


@router.post("/apply-service-preset", response_model=OnboardingStatusOut)
async def apply_service_preset(
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OnboardingStatusOut:
    """Apply common services preset. Idempotent - won't duplicate existing services."""
    org_id = manager_user.organization_id

    # Get first location (required for services)
    first_location = await db.scalar(
        select(Location.id).where(Location.organization_id == org_id).limit(1)
    )

    if not first_location:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Primero debes crear una sucursal",
        )

    # Get existing service names for this location
    existing_services = await db.execute(
        select(Service.name).where(
            Service.organization_id == org_id,
            Service.location_id == first_location,
        )
    )
    existing_names = {name.lower() for (name,) in existing_services.all()}

    # Create missing services
    for service_data in DEFAULT_SERVICES_PRESET:
        if service_data["name"].lower() not in existing_names:
            new_service = Service(
                organization_id=org_id,
                location_id=first_location,
                name=service_data["name"],
                price_mxn=service_data["price_mxn"],
                active=True,
                sort_order=service_data["sort_order"],
            )
            db.add(new_service)

    await db.flush()

    return await get_onboarding_status(manager_user, db)
