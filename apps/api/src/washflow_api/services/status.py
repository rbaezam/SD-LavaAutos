"""Status service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.models import Status
from washflow_api.schemas.status import StatusCreate, StatusUpdate


class StatusService:
    """Service for managing workflow statuses."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_statuses(
        self,
        location_id: str,
        organization_id: str,
    ) -> tuple[list[Status], int]:
        """List all statuses for a location ordered by sort_order."""
        query = (
            select(Status)
            .where(
                Status.location_id == location_id,
                Status.organization_id == organization_id,
            )
            .order_by(Status.sort_order)
        )

        result = await self.db.execute(query)
        statuses = list(result.scalars().all())

        # Count
        count_query = select(func.count(Status.id)).where(
            Status.location_id == location_id,
            Status.organization_id == organization_id,
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return statuses, total

    async def get_status(
        self,
        status_id: str,
        organization_id: str,
    ) -> Status | None:
        """Get a status by ID, ensuring it belongs to the organization."""
        result = await self.db.execute(
            select(Status).where(
                Status.id == status_id,
                Status.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_status(
        self,
        data: StatusCreate,
        location_id: str,
        organization_id: str,
    ) -> Status:
        """Create a new status."""
        # Check for duplicate name
        existing = await self._get_status_by_name(
            location_id, data.name, organization_id
        )
        if existing:
            raise ValueError(f"Ya existe un estado con el nombre '{data.name}'")

        # Get next sort_order
        next_order = await self._get_next_sort_order(location_id, organization_id)

        status = Status(
            organization_id=organization_id,
            location_id=location_id,
            name=data.name,
            is_terminal=data.is_terminal,
            sort_order=next_order,
        )
        self.db.add(status)
        await self.db.flush()
        await self.db.refresh(status)
        return status

    async def update_status(
        self,
        status: Status,
        data: StatusUpdate,
    ) -> Status:
        """Update a status."""
        # Check for duplicate name if name is being changed
        if data.name is not None and data.name != status.name:
            existing = await self._get_status_by_name(
                status.location_id, data.name, status.organization_id
            )
            if existing and existing.id != status.id:
                raise ValueError(f"Ya existe un estado con el nombre '{data.name}'")

        if data.name is not None:
            status.name = data.name
        if data.is_terminal is not None:
            status.is_terminal = data.is_terminal

        await self.db.flush()
        await self.db.refresh(status)
        return status

    async def reorder_statuses(
        self,
        location_id: str,
        organization_id: str,
        ordered_ids: list[str],
    ) -> list[Status]:
        """Reorder statuses by setting sort_order based on position in list."""
        # Validate all IDs belong to the location
        result = await self.db.execute(
            select(Status).where(
                Status.location_id == location_id,
                Status.organization_id == organization_id,
            )
        )
        existing_statuses = {s.id: s for s in result.scalars().all()}

        # Verify all provided IDs exist in the location
        for status_id in ordered_ids:
            if status_id not in existing_statuses:
                raise ValueError(f"Estado no encontrado: {status_id}")

        # Update sort_order for each status
        updated_statuses = []
        for index, status_id in enumerate(ordered_ids):
            status = existing_statuses[status_id]
            status.sort_order = index
            updated_statuses.append(status)

        await self.db.flush()

        # Refresh all statuses
        for status in updated_statuses:
            await self.db.refresh(status)

        # Return in order
        return sorted(updated_statuses, key=lambda s: s.sort_order)

    async def _get_status_by_name(
        self,
        location_id: str,
        name: str,
        organization_id: str,
    ) -> Status | None:
        """Get a status by name within a location."""
        result = await self.db.execute(
            select(Status).where(
                Status.location_id == location_id,
                Status.organization_id == organization_id,
                Status.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def _get_next_sort_order(
        self,
        location_id: str,
        organization_id: str,
    ) -> int:
        """Get the next sort_order value for a location."""
        result = await self.db.execute(
            select(func.max(Status.sort_order)).where(
                Status.location_id == location_id,
                Status.organization_id == organization_id,
            )
        )
        max_order = result.scalar()
        return (max_order or -1) + 1
