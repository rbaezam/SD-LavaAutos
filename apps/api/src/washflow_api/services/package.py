"""Package service."""

import logging
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from washflow_api.models import Package, PackageService, Service, VehicleType
from washflow_api.schemas.package import PackageCreate, PackageUpdate

logger = logging.getLogger(__name__)


class PackageServiceBiz:
    """Business logic service for packages."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_packages(
        self,
        organization_id: str,
        vehicle_type_id: str | None = None,
        include_inactive: bool = False,
    ) -> list[Package]:
        """List packages for an organization."""
        query = (
            select(Package)
            .where(Package.organization_id == organization_id)
            .options(
                selectinload(Package.vehicle_type),
                selectinload(Package.services).selectinload(PackageService.service),
            )
        )

        if vehicle_type_id:
            query = query.where(Package.vehicle_type_id == vehicle_type_id)

        if not include_inactive:
            query = query.where(Package.is_active == True)  # noqa: E712

        query = query.order_by(Package.sort_order, Package.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_package(
        self,
        package_id: str,
        organization_id: str,
    ) -> Package | None:
        """Get a package by ID with all relations loaded."""
        result = await self.db.execute(
            select(Package)
            .where(
                Package.id == package_id,
                Package.organization_id == organization_id,
            )
            .options(
                selectinload(Package.vehicle_type),
                selectinload(Package.services).selectinload(PackageService.service),
            )
        )
        return result.scalar_one_or_none()

    async def create_package(
        self,
        organization_id: str,
        data: PackageCreate,
    ) -> Package:
        """Create a new package with services."""
        # Validate vehicle type exists
        vt_result = await self.db.execute(
            select(VehicleType).where(
                VehicleType.id == data.vehicle_type_id,
                VehicleType.organization_id == organization_id,
            )
        )
        vehicle_type = vt_result.scalar_one_or_none()
        if not vehicle_type:
            raise ValueError("Tipo de vehículo no encontrado")

        # Get next sort order if not specified
        if data.sort_order == 0:
            result = await self.db.execute(
                select(func.coalesce(func.max(Package.sort_order), -1) + 1).where(
                    Package.organization_id == organization_id
                )
            )
            next_order = result.scalar() or 0
        else:
            next_order = data.sort_order

        # Create package
        package = Package(
            id=str(uuid4()),
            organization_id=organization_id,
            name=data.name,
            description=data.description,
            base_price_mxn=data.base_price_mxn,
            vehicle_type_id=data.vehicle_type_id,
            workers_required=data.workers_required,
            estimated_duration_minutes=data.estimated_duration_minutes,
            commission_per_worker_mxn=data.commission_per_worker_mxn,
            is_active=data.is_active,
            sort_order=next_order,
        )

        self.db.add(package)
        await self.db.flush()

        # Add services if provided
        if data.service_ids:
            await self._set_package_services(
                package.id, organization_id, data.service_ids
            )

        await self.db.refresh(package)

        return await self.get_package(package.id, organization_id)  # type: ignore

    async def update_package(
        self,
        package_id: str,
        organization_id: str,
        data: PackageUpdate,
    ) -> Package:
        """Update a package."""
        package = await self.get_package(package_id, organization_id)
        if not package:
            raise ValueError("Paquete no encontrado")

        # Validate vehicle type if being changed
        if data.vehicle_type_id is not None:
            vt_result = await self.db.execute(
                select(VehicleType).where(
                    VehicleType.id == data.vehicle_type_id,
                    VehicleType.organization_id == organization_id,
                )
            )
            if not vt_result.scalar_one_or_none():
                raise ValueError("Tipo de vehículo no encontrado")

        # Handle service_ids separately
        service_ids = data.service_ids
        update_data = data.model_dump(exclude_unset=True, exclude={"service_ids"})

        for field, value in update_data.items():
            setattr(package, field, value)

        # Update services if provided
        if service_ids is not None:
            # Delete existing services
            for ps in package.services:
                await self.db.delete(ps)

            # Add new services
            await self._set_package_services(package_id, organization_id, service_ids)

        await self.db.flush()

        return await self.get_package(package_id, organization_id)  # type: ignore

    async def delete_package(
        self,
        package_id: str,
        organization_id: str,
    ) -> bool:
        """Delete a package (soft delete by deactivating)."""
        package = await self.get_package(package_id, organization_id)
        if not package:
            return False

        # Soft delete - just deactivate
        package.is_active = False
        await self.db.flush()

        return True

    async def _set_package_services(
        self,
        package_id: str,
        organization_id: str,
        service_ids: list[str],
    ) -> None:
        """Set services for a package."""
        if not service_ids:
            return

        # Validate services exist and belong to organization
        result = await self.db.execute(
            select(Service).where(
                Service.id.in_(service_ids),
                Service.organization_id == organization_id,
            )
        )
        valid_services = {s.id for s in result.scalars().all()}

        # Create package services in order
        for idx, service_id in enumerate(service_ids):
            if service_id in valid_services:
                package_service = PackageService(
                    id=str(uuid4()),
                    package_id=package_id,
                    service_id=service_id,
                    sort_order=idx,
                )
                self.db.add(package_service)

    async def get_packages_for_vehicle_type(
        self,
        organization_id: str,
        vehicle_type_id: str,
    ) -> list[Package]:
        """Get active packages for a specific vehicle type."""
        return await self.list_packages(
            organization_id=organization_id,
            vehicle_type_id=vehicle_type_id,
            include_inactive=False,
        )
