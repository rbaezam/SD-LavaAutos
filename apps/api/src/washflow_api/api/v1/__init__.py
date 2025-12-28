"""API v1 module."""

from fastapi import APIRouter

from washflow_api.api.v1.endpoints import (
    auth,
    dashboard,
    health,
    locations,
    notifications,
    onboarding,
    org,
    packages,
    public,
    services,
    statuses,
    tickets,
    vehicle_types,
)

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(org.router, prefix="/org", tags=["organization"])
router.include_router(
    onboarding.router, prefix="/org/onboarding", tags=["onboarding"]
)
router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
router.include_router(locations.router, prefix="/locations", tags=["locations"])
router.include_router(services.router, tags=["services"])
router.include_router(statuses.router, tags=["statuses"])
router.include_router(
    vehicle_types.router, prefix="/vehicle-types", tags=["vehicle-types"]
)
router.include_router(packages.router, prefix="/packages", tags=["packages"])
router.include_router(tickets.router, tags=["tickets"])
router.include_router(public.router, prefix="/public", tags=["public"])
router.include_router(
    notifications.router, prefix="/notifications", tags=["notifications"]
)
