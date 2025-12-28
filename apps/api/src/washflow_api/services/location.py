"""Location service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.models import Location, Status
from washflow_api.schemas.location import LocationCreate, LocationUpdate

# Default statuses to seed when creating a new location
DEFAULT_STATUSES = [
    {"name": "En espera", "sort_order": 0, "is_terminal": False},
    {"name": "En lavado", "sort_order": 1, "is_terminal": False},
    {"name": "En secado", "sort_order": 2, "is_terminal": False},
    {"name": "Detallado", "sort_order": 3, "is_terminal": False},
    {"name": "Listo", "sort_order": 4, "is_terminal": False},
    {"name": "Entregado", "sort_order": 5, "is_terminal": True},
]


class LocationService:
    """Service for location operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_locations(
        self,
        organization_id: str,
        include_inactive: bool = False,
    ) -> tuple[list[Location], int]:
        """List all locations for an organization."""
        query = select(Location).where(Location.organization_id == organization_id)

        if not include_inactive:
            query = query.where(Location.is_active == True)  # noqa: E712

        query = query.order_by(Location.name)

        result = await self.db.execute(query)
        locations = list(result.scalars().all())

        # Count query
        count_query = select(func.count(Location.id)).where(
            Location.organization_id == organization_id
        )
        if not include_inactive:
            count_query = count_query.where(Location.is_active == True)  # noqa: E712

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return locations, total

    async def get_location(
        self,
        location_id: str,
        organization_id: str,
    ) -> Location | None:
        """Get a location by ID, ensuring it belongs to the organization."""
        result = await self.db.execute(
            select(Location).where(
                Location.id == location_id,
                Location.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_location(
        self,
        data: LocationCreate,
        organization_id: str,
    ) -> Location:
        """Create a new location and seed default statuses."""
        location = Location(
            organization_id=organization_id,
            name=data.name,
            address=data.address,
        )
        self.db.add(location)
        await self.db.flush()
        await self.db.refresh(location)

        # Seed default statuses
        await self._seed_default_statuses(location.id, organization_id)

        return location

    async def update_location(
        self,
        location: Location,
        data: LocationUpdate,
    ) -> Location:
        """Update a location."""
        if data.name is not None:
            location.name = data.name
        if data.address is not None:
            location.address = data.address

        await self.db.flush()
        await self.db.refresh(location)
        return location

    async def delete_location(self, location: Location) -> None:
        """Delete a location (hard delete)."""
        await self.db.delete(location)
        await self.db.flush()

    async def _seed_default_statuses(
        self,
        location_id: str,
        organization_id: str,
    ) -> None:
        """Seed default statuses for a new location."""
        for status_data in DEFAULT_STATUSES:
            status = Status(
                organization_id=organization_id,
                location_id=location_id,
                name=status_data["name"],
                sort_order=status_data["sort_order"],
                is_terminal=status_data["is_terminal"],
            )
            self.db.add(status)
        await self.db.flush()
