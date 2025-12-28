"""Vehicle type service."""

import logging
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.models import VehicleType
from washflow_api.schemas.vehicle_type import VehicleTypeCreate, VehicleTypeUpdate

logger = logging.getLogger(__name__)


class VehicleTypeService:
    """Business logic service for vehicle types."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_vehicle_types(
        self,
        organization_id: str,
        include_inactive: bool = False,
    ) -> list[VehicleType]:
        """List vehicle types for an organization."""
        query = select(VehicleType).where(
            VehicleType.organization_id == organization_id
        )

        if not include_inactive:
            query = query.where(VehicleType.is_active == True)  # noqa: E712

        query = query.order_by(VehicleType.sort_order, VehicleType.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_vehicle_type(
        self,
        vehicle_type_id: str,
        organization_id: str,
    ) -> VehicleType | None:
        """Get a vehicle type by ID."""
        result = await self.db.execute(
            select(VehicleType).where(
                VehicleType.id == vehicle_type_id,
                VehicleType.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_vehicle_type(
        self,
        organization_id: str,
        data: VehicleTypeCreate,
    ) -> VehicleType:
        """Create a new vehicle type."""
        # Get next sort order if not specified
        if data.sort_order == 0:
            result = await self.db.execute(
                select(func.coalesce(func.max(VehicleType.sort_order), -1) + 1).where(
                    VehicleType.organization_id == organization_id
                )
            )
            next_order = result.scalar() or 0
        else:
            next_order = data.sort_order

        vehicle_type = VehicleType(
            id=str(uuid4()),
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            default_workers=data.default_workers,
            default_duration_minutes=data.default_duration_minutes,
            is_active=data.is_active,
            sort_order=next_order,
        )

        self.db.add(vehicle_type)
        await self.db.flush()
        await self.db.refresh(vehicle_type)

        return vehicle_type

    async def update_vehicle_type(
        self,
        vehicle_type_id: str,
        organization_id: str,
        data: VehicleTypeUpdate,
    ) -> VehicleType:
        """Update a vehicle type."""
        vehicle_type = await self.get_vehicle_type(vehicle_type_id, organization_id)
        if not vehicle_type:
            raise ValueError("Tipo de vehículo no encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle_type, field, value)

        await self.db.flush()
        await self.db.refresh(vehicle_type)

        return vehicle_type

    async def delete_vehicle_type(
        self,
        vehicle_type_id: str,
        organization_id: str,
    ) -> bool:
        """Delete a vehicle type (soft delete by deactivating)."""
        vehicle_type = await self.get_vehicle_type(vehicle_type_id, organization_id)
        if not vehicle_type:
            return False

        # Soft delete - just deactivate
        vehicle_type.is_active = False
        await self.db.flush()

        return True

    async def reorder_vehicle_types(
        self,
        organization_id: str,
        vehicle_type_ids: list[str],
    ) -> list[VehicleType]:
        """Reorder vehicle types."""
        vehicle_types = await self.list_vehicle_types(
            organization_id, include_inactive=True
        )
        id_to_vt = {vt.id: vt for vt in vehicle_types}

        for idx, vt_id in enumerate(vehicle_type_ids):
            if vt_id in id_to_vt:
                id_to_vt[vt_id].sort_order = idx

        await self.db.flush()

        return await self.list_vehicle_types(organization_id, include_inactive=True)
