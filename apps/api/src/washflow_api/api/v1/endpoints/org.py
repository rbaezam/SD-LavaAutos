"""Organization endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser, ManagerUser
from washflow_api.db import get_db
from washflow_api.models import Location
from washflow_api.schemas.organization import (
    BrandingOut,
    BrandingUpdate,
    LocationBrandingOut,
    LocationBrandingUpdate,
    OrgMeResponse,
    OrganizationOut,
)

router = APIRouter()


@router.get("/me", response_model=OrgMeResponse)
async def get_my_organization(current_user: CurrentUser) -> OrgMeResponse:
    """Get current user's organization info and role."""
    org = current_user.organization
    location = current_user.location

    return OrgMeResponse(
        organization=OrganizationOut(
            id=org.id,
            name=org.name,
            created_at=org.created_at,
        ),
        role=current_user.role,
        location_id=current_user.location_id,
        location_name=location.name if location else None,
    )


# Branding endpoints (manager only)
@router.get("/branding", response_model=BrandingOut)
async def get_branding(manager_user: ManagerUser) -> BrandingOut:
    """Get organization branding settings."""
    org = manager_user.organization
    return BrandingOut(
        brand_name=org.brand_name,
        brand_logo_url=org.brand_logo_url,
        brand_primary_color=org.brand_primary_color,
    )


@router.patch("/branding", response_model=BrandingOut)
async def update_branding(
    data: BrandingUpdate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BrandingOut:
    """Update organization branding settings."""
    org = manager_user.organization

    # Update fields if provided (explicit None is allowed to clear)
    if data.brand_name is not None:
        org.brand_name = data.brand_name if data.brand_name else None
    if data.brand_logo_url is not None:
        org.brand_logo_url = data.brand_logo_url if data.brand_logo_url else None
    if data.brand_primary_color is not None:
        org.brand_primary_color = (
            data.brand_primary_color if data.brand_primary_color else None
        )

    await db.flush()
    await db.refresh(org)

    return BrandingOut(
        brand_name=org.brand_name,
        brand_logo_url=org.brand_logo_url,
        brand_primary_color=org.brand_primary_color,
    )


@router.get("/locations/{location_id}/branding", response_model=LocationBrandingOut)
async def get_location_branding(
    location_id: str,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationBrandingOut:
    """Get branding overrides for a specific location."""
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.organization_id == manager_user.organization_id,
        )
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    return LocationBrandingOut(
        location_id=location.id,
        location_name=location.name,
        brand_name_override=location.brand_name_override,
        brand_logo_url_override=location.brand_logo_url_override,
        brand_primary_color_override=location.brand_primary_color_override,
    )


@router.patch("/locations/{location_id}/branding", response_model=LocationBrandingOut)
async def update_location_branding(
    location_id: str,
    data: LocationBrandingUpdate,
    manager_user: ManagerUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LocationBrandingOut:
    """Update branding overrides for a specific location."""
    result = await db.execute(
        select(Location).where(
            Location.id == location_id,
            Location.organization_id == manager_user.organization_id,
        )
    )
    location = result.scalar_one_or_none()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sucursal no encontrada",
        )

    # Update fields if provided
    if data.brand_name_override is not None:
        location.brand_name_override = (
            data.brand_name_override if data.brand_name_override else None
        )
    if data.brand_logo_url_override is not None:
        location.brand_logo_url_override = (
            data.brand_logo_url_override if data.brand_logo_url_override else None
        )
    if data.brand_primary_color_override is not None:
        location.brand_primary_color_override = (
            data.brand_primary_color_override
            if data.brand_primary_color_override
            else None
        )

    await db.flush()
    await db.refresh(location)

    return LocationBrandingOut(
        location_id=location.id,
        location_name=location.name,
        brand_name_override=location.brand_name_override,
        brand_logo_url_override=location.brand_logo_url_override,
        brand_primary_color_override=location.brand_primary_color_override,
    )
