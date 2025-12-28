"""Dashboard service for metrics and analytics."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.models import Status, Ticket, TicketEvent
from washflow_api.schemas.dashboard import (
    DashboardFlow,
    DashboardSummary,
    DashboardTimeline,
    DateRange,
    StatusFlowItem,
    TimelinePoint,
)

# Default timezone for Mexico
DEFAULT_TZ = ZoneInfo("America/Mexico_City")


class DashboardService:
    """Service for dashboard metrics."""

    def __init__(self, db: AsyncSession, timezone: ZoneInfo = DEFAULT_TZ):
        self.db = db
        self.tz = timezone

    def _get_date_range(
        self,
        range_type: DateRange,
        from_date: date | None,
        to_date: date | None,
    ) -> tuple[datetime, datetime]:
        """Get start and end datetime for the given range."""
        now = datetime.now(self.tz)
        today = now.date()

        if range_type == DateRange.HOY:
            start = datetime.combine(today, datetime.min.time(), tzinfo=self.tz)
            end = now
        elif range_type == DateRange.AYER:
            yesterday = today - timedelta(days=1)
            start = datetime.combine(yesterday, datetime.min.time(), tzinfo=self.tz)
            end = datetime.combine(today, datetime.min.time(), tzinfo=self.tz)
        elif range_type == DateRange.ULTIMOS_7_DIAS:
            start_date = today - timedelta(days=6)
            start = datetime.combine(start_date, datetime.min.time(), tzinfo=self.tz)
            end = now
        elif range_type == DateRange.PERSONALIZADO:
            if not from_date or not to_date:
                # Fallback to today
                start = datetime.combine(today, datetime.min.time(), tzinfo=self.tz)
                end = now
            else:
                start = datetime.combine(from_date, datetime.min.time(), tzinfo=self.tz)
                # End of to_date day
                end = datetime.combine(
                    to_date + timedelta(days=1), datetime.min.time(), tzinfo=self.tz
                )
        else:
            start = datetime.combine(today, datetime.min.time(), tzinfo=self.tz)
            end = now

        return start, end

    async def get_summary(
        self,
        location_id: str,
        organization_id: str,
        range_type: DateRange,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> DashboardSummary:
        """Get dashboard summary metrics."""
        start, end = self._get_date_range(range_type, from_date, to_date)

        # Base query for tickets in range
        base_filter = [
            Ticket.location_id == location_id,
            Ticket.organization_id == organization_id,
            Ticket.created_at >= start,
            Ticket.created_at < end,
        ]

        # Total tickets
        total_result = await self.db.execute(
            select(func.count(Ticket.id)).where(*base_filter)
        )
        total_tickets = total_result.scalar() or 0

        # Completed (terminal status)
        completed_result = await self.db.execute(
            select(func.count(Ticket.id))
            .join(Status, Ticket.current_status_id == Status.id)
            .where(*base_filter, Status.is_terminal.is_(True))
        )
        completed = completed_result.scalar() or 0

        # In progress (non-terminal)
        in_progress = total_tickets - completed

        # Average time to completion (only for completed tickets with completed_at)
        # Also count how many tickets were used for the average
        avg_result = await self.db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        Ticket.completed_at - Ticket.created_at,
                    )
                    / 60
                ),
                func.count(Ticket.id),
            )
            .join(Status, Ticket.current_status_id == Status.id)
            .where(
                *base_filter,
                Status.is_terminal.is_(True),
                Ticket.completed_at.isnot(None),
            )
        )
        row = avg_result.one()
        avg_minutes_raw = row[0]
        avg_sample_size = row[1] or 0
        avg_total_minutes = round(avg_minutes_raw) if avg_minutes_raw else None

        # Throughput per hour
        throughput_per_hour: float | None = None
        if completed > 0:
            now_tz = datetime.now(self.tz)
            if range_type == DateRange.HOY:
                # Hours since 8:00 AM (assumed business start)
                business_start = datetime.combine(
                    now_tz.date(), datetime.min.time(), tzinfo=self.tz
                ).replace(hour=8)
                if now_tz < business_start:
                    hours_elapsed = 1.0
                else:
                    hours_elapsed = max(
                        1.0, (now_tz - business_start).total_seconds() / 3600
                    )
            elif range_type == DateRange.AYER:
                # Full day = assume 10 business hours
                hours_elapsed = 10.0
            else:
                # For multi-day ranges, use 10 hours per day
                days = (end - start).days or 1
                hours_elapsed = days * 10.0

            throughput_per_hour = round(completed / hours_elapsed, 1)

        return DashboardSummary(
            range=range_type.value,
            from_date=start.date(),
            to_date=(end - timedelta(seconds=1)).date(),
            total_tickets=total_tickets,
            in_progress=in_progress,
            completed=completed,
            avg_total_minutes=avg_total_minutes,
            avg_sample_size=avg_sample_size,
            throughput_per_hour=throughput_per_hour,
        )

    async def get_flow(
        self,
        location_id: str,
        organization_id: str,
        range_type: DateRange,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> DashboardFlow:
        """Get ticket count per status (flow view)."""
        start, end = self._get_date_range(range_type, from_date, to_date)

        # Get all statuses for the location with ticket counts
        result = await self.db.execute(
            select(
                Status.id,
                Status.name,
                Status.sort_order,
                func.count(Ticket.id).label("ticket_count"),
            )
            .outerjoin(
                Ticket,
                (Ticket.current_status_id == Status.id)
                & (Ticket.location_id == location_id)
                & (Ticket.organization_id == organization_id)
                & (Ticket.created_at >= start)
                & (Ticket.created_at < end),
            )
            .where(
                Status.location_id == location_id,
                Status.organization_id == organization_id,
            )
            .group_by(Status.id, Status.name, Status.sort_order)
            .order_by(Status.sort_order)
        )

        statuses = []
        for row in result.all():
            statuses.append(
                StatusFlowItem(
                    status_id=row.id,
                    name=row.name,
                    count=row.ticket_count or 0,
                    sort_order=row.sort_order,
                )
            )

        return DashboardFlow(statuses=statuses)

    async def get_timeline(
        self,
        location_id: str,
        organization_id: str,
        range_type: DateRange,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> DashboardTimeline:
        """Get ticket creation timeline (hourly or daily)."""
        start, end = self._get_date_range(range_type, from_date, to_date)

        # Determine bucket type
        days_diff = (end - start).days
        use_hourly = days_diff <= 2

        if use_hourly:
            # Group by hour
            # Convert to local timezone for grouping
            hour_expr = func.date_trunc(
                "hour",
                func.timezone(str(self.tz), Ticket.created_at),
            )

            result = await self.db.execute(
                select(hour_expr.label("bucket"), func.count(Ticket.id).label("cnt"))
                .where(
                    Ticket.location_id == location_id,
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= start,
                    Ticket.created_at < end,
                )
                .group_by(hour_expr)
                .order_by(hour_expr)
            )

            # Build complete hourly buckets (0-23 for today/yesterday)
            counts_by_hour: dict[int, int] = {}
            for row in result.all():
                if row.bucket:
                    hour = row.bucket.hour
                    counts_by_hour[hour] = row.cnt

            # Generate all hours
            points = []
            if range_type == DateRange.HOY:
                # Only up to current hour
                current_hour = datetime.now(self.tz).hour
                for h in range(24):
                    if h <= current_hour:
                        points.append(
                            TimelinePoint(
                                label=f"{h:02d}:00", count=counts_by_hour.get(h, 0)
                            )
                        )
            else:
                # Full 24 hours for yesterday or short custom range
                for h in range(24):
                    points.append(
                        TimelinePoint(
                            label=f"{h:02d}:00", count=counts_by_hour.get(h, 0)
                        )
                    )

            return DashboardTimeline(bucket="hour", points=points)
        else:
            # Group by day
            day_expr = func.date(
                func.timezone(str(self.tz), Ticket.created_at),
            )

            result = await self.db.execute(
                select(day_expr.label("bucket"), func.count(Ticket.id).label("cnt"))
                .where(
                    Ticket.location_id == location_id,
                    Ticket.organization_id == organization_id,
                    Ticket.created_at >= start,
                    Ticket.created_at < end,
                )
                .group_by(day_expr)
                .order_by(day_expr)
            )

            counts_by_day: dict[date, int] = {}
            for row in result.all():
                if row.bucket:
                    counts_by_day[row.bucket] = row.cnt

            # Generate all days in range
            points = []
            current_date = start.date()
            end_date = (end - timedelta(seconds=1)).date()
            while current_date <= end_date:
                points.append(
                    TimelinePoint(
                        label=current_date.strftime("%d/%m"),
                        count=counts_by_day.get(current_date, 0),
                    )
                )
                current_date += timedelta(days=1)

            return DashboardTimeline(bucket="day", points=points)
