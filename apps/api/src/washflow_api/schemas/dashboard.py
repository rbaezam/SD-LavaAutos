"""Dashboard schemas."""

from datetime import date
from enum import Enum

from pydantic import BaseModel


class DateRange(str, Enum):
    """Date range options for dashboard."""

    HOY = "hoy"
    AYER = "ayer"
    ULTIMOS_7_DIAS = "ultimos_7_dias"
    PERSONALIZADO = "personalizado"


class DashboardSummary(BaseModel):
    """Dashboard summary response."""

    range: str
    from_date: date
    to_date: date
    total_tickets: int
    in_progress: int
    completed: int
    avg_total_minutes: int | None
    avg_sample_size: int  # Number of completed tickets used for avg calculation
    throughput_per_hour: float | None


class StatusFlowItem(BaseModel):
    """Single status in the flow."""

    status_id: str
    name: str
    count: int
    sort_order: int


class DashboardFlow(BaseModel):
    """Dashboard flow response - tickets per status."""

    statuses: list[StatusFlowItem]


class TimelinePoint(BaseModel):
    """Single point in the timeline."""

    label: str
    count: int


class DashboardTimeline(BaseModel):
    """Dashboard timeline response."""

    bucket: str  # "hour" or "day"
    points: list[TimelinePoint]
