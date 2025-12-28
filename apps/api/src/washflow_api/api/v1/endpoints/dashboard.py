"""Dashboard endpoints."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.api.deps import CurrentUser
from washflow_api.db import get_db
from washflow_api.schemas.dashboard import (
    DashboardFlow,
    DashboardSummary,
    DashboardTimeline,
    DateRange,
)
from washflow_api.services.dashboard import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    range: DateRange = Query(default=DateRange.HOY, alias="range"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> DashboardSummary:
    """
    Get dashboard summary metrics.

    - **range**: hoy, ayer, ultimos_7_dias, personalizado
    - **from/to**: Required if range is 'personalizado'

    Returns KPIs: total tickets, in progress, completed, avg time, throughput.
    """
    service = DashboardService(db)
    return await service.get_summary(
        location_id=current_user.location_id,
        organization_id=current_user.organization_id,
        range_type=range,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/flow", response_model=DashboardFlow)
async def get_dashboard_flow(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    range: DateRange = Query(default=DateRange.HOY, alias="range"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> DashboardFlow:
    """
    Get ticket distribution across statuses.

    Returns count of tickets per status for the flow visualization.
    """
    service = DashboardService(db)
    return await service.get_flow(
        location_id=current_user.location_id,
        organization_id=current_user.organization_id,
        range_type=range,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/timeline", response_model=DashboardTimeline)
async def get_dashboard_timeline(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    range: DateRange = Query(default=DateRange.HOY, alias="range"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
) -> DashboardTimeline:
    """
    Get ticket creation timeline.

    - Hourly buckets for 'hoy', 'ayer', or ranges <= 2 days
    - Daily buckets for longer ranges

    Always returns complete buckets (with 0 counts for empty periods).
    """
    service = DashboardService(db)
    return await service.get_timeline(
        location_id=current_user.location_id,
        organization_id=current_user.organization_id,
        range_type=range,
        from_date=from_date,
        to_date=to_date,
    )
