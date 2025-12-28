"""Service catalog service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.models import Service
from washflow_api.schemas.service import ServiceCreate, ServiceUpdate


class ServiceCatalogService:
    """Service for managing service catalog."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_services(
        self,
        location_id: str,
        organization_id: str,
        include_inactive: bool = False,
    ) -> tuple[list[Service], int]:
        """List all services for a location."""
        query = select(Service).where(
            Service.location_id == location_id,
            Service.organization_id == organization_id,
        )

        if not include_inactive:
            query = query.where(Service.active == True)  # noqa: E712

        query = query.order_by(Service.sort_order, Service.name)

        result = await self.db.execute(query)
        services = list(result.scalars().all())

        # Count query
        count_query = select(func.count(Service.id)).where(
            Service.location_id == location_id,
            Service.organization_id == organization_id,
        )
        if not include_inactive:
            count_query = count_query.where(Service.active == True)  # noqa: E712

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return services, total

    async def get_service(
        self,
        service_id: str,
        organization_id: str,
    ) -> Service | None:
        """Get a service by ID, ensuring it belongs to the organization."""
        result = await self.db.execute(
            select(Service).where(
                Service.id == service_id,
                Service.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_service(
        self,
        data: ServiceCreate,
        location_id: str,
        organization_id: str,
    ) -> Service:
        """Create a new service."""
        # Check for duplicate name among active services
        existing = await self._get_active_service_by_name(
            location_id, data.name, organization_id
        )
        if existing:
            raise ValueError(f"Ya existe un servicio activo con el nombre '{data.name}'")

        service = Service(
            organization_id=organization_id,
            location_id=location_id,
            name=data.name,
            price_mxn=data.price_mxn,
            duration_minutes=data.duration_minutes,
            sort_order=data.sort_order,
            active=True,
        )
        self.db.add(service)
        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def update_service(
        self,
        service: Service,
        data: ServiceUpdate,
    ) -> Service:
        """Update a service."""
        # Check for duplicate name if name is being changed
        if data.name is not None and data.name != service.name and service.active:
            existing = await self._get_active_service_by_name(
                service.location_id, data.name, service.organization_id
            )
            if existing and existing.id != service.id:
                raise ValueError(f"Ya existe un servicio activo con el nombre '{data.name}'")

        if data.name is not None:
            service.name = data.name
        if data.price_mxn is not None:
            service.price_mxn = data.price_mxn
        if data.duration_minutes is not None:
            service.duration_minutes = data.duration_minutes
        if data.sort_order is not None:
            service.sort_order = data.sort_order

        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def activate_service(self, service: Service) -> Service:
        """Activate a service."""
        # Check for duplicate name when activating
        existing = await self._get_active_service_by_name(
            service.location_id, service.name, service.organization_id
        )
        if existing and existing.id != service.id:
            raise ValueError(
                f"No se puede activar: ya existe un servicio activo con el nombre '{service.name}'"
            )

        service.active = True
        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def deactivate_service(self, service: Service) -> Service:
        """Deactivate a service."""
        service.active = False
        await self.db.flush()
        await self.db.refresh(service)
        return service

    async def _get_active_service_by_name(
        self,
        location_id: str,
        name: str,
        organization_id: str,
    ) -> Service | None:
        """Get an active service by name within a location."""
        result = await self.db.execute(
            select(Service).where(
                Service.location_id == location_id,
                Service.organization_id == organization_id,
                Service.name == name,
                Service.active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()
