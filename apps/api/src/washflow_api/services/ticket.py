"""Ticket service."""

import logging
import secrets
import string
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from washflow_api.models import (
    EventType,
    Package,
    PackageService,
    Service,
    Status,
    Ticket,
    TicketEvent,
    TicketService,
    User,
    VehicleType,
)
from washflow_api.models.notification import NotificationEvent
from washflow_api.schemas.ticket import TicketCreate, TicketUpdate

logger = logging.getLogger(__name__)


def generate_public_code() -> str:
    """Generate a random public code like WF-2K9A."""
    # Use uppercase letters and digits, excluding confusing chars (0, O, I, L, 1)
    alphabet = string.ascii_uppercase.replace("O", "").replace("I", "").replace("L", "")
    digits = string.digits.replace("0", "").replace("1", "")
    chars = alphabet + digits
    code = "".join(secrets.choice(chars) for _ in range(4))
    return f"WF-{code}"


class TicketServiceBiz:
    """Business logic service for tickets."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_tickets(
        self,
        location_id: str,
        organization_id: str,
        status_id: str | None = None,
        search: str | None = None,
        date_filter: str | None = None,  # "today" or None for all
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Ticket], int]:
        """List tickets for a location with filters."""
        # Base query
        query = (
            select(Ticket)
            .where(
                Ticket.location_id == location_id,
                Ticket.organization_id == organization_id,
            )
            .options(
                selectinload(Ticket.current_status),
                selectinload(Ticket.services),
            )
        )

        # Filter by status
        if status_id:
            query = query.where(Ticket.current_status_id == status_id)

        # Filter by date
        if date_filter == "today":
            today_start = datetime.now(UTC).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)
            query = query.where(
                Ticket.created_at >= today_start,
                Ticket.created_at < today_end,
            )

        # Search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Ticket.public_code.ilike(search_term),
                    Ticket.plate.ilike(search_term),
                    Ticket.vehicle_desc.ilike(search_term),
                    Ticket.manual_ticket_no.ilike(search_term),
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # Order by newest first and paginate
        query = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        tickets = list(result.scalars().all())

        return tickets, total

    async def get_ticket(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> Ticket | None:
        """Get a ticket by ID with all relations loaded."""
        result = await self.db.execute(
            select(Ticket)
            .where(
                Ticket.id == ticket_id,
                Ticket.organization_id == organization_id,
            )
            .options(
                selectinload(Ticket.current_status),
                selectinload(Ticket.services),
                selectinload(Ticket.events).selectinload(TicketEvent.actor),
                selectinload(Ticket.events).selectinload(TicketEvent.from_status),
                selectinload(Ticket.events).selectinload(TicketEvent.to_status),
            )
        )
        return result.scalar_one_or_none()

    async def get_ticket_by_public_code(
        self,
        public_code: str,
    ) -> Ticket | None:
        """Get a ticket by public code (for public access - no org filter)."""
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.public_code == public_code)
            .options(
                selectinload(Ticket.current_status),
                selectinload(Ticket.location),
                selectinload(Ticket.organization),
                selectinload(Ticket.services),
            )
        )
        return result.scalar_one_or_none()

    async def create_ticket(
        self,
        data: TicketCreate,
        location_id: str,
        organization_id: str,
        actor: User,
    ) -> Ticket:
        """Create a new ticket with services snapshot."""
        # Get the first status for the location
        first_status = await self._get_first_status(location_id, organization_id)
        if not first_status:
            raise ValueError(
                "No hay estados configurados para esta sucursal. "
                "Por favor, configure los estados primero."
            )

        # Generate unique public code
        public_code = await self._generate_unique_public_code(organization_id)

        # Package-based creation (preferred)
        package: Package | None = None
        vehicle_type: VehicleType | None = None
        services: list[Service] = []
        total_duration = 0
        captured_package_name: str | None = None
        captured_package_price_mxn: int | None = None
        captured_workers_required: int | None = None
        captured_estimated_duration_minutes: int | None = None

        if data.package_id:
            # Get package with services
            package = await self._get_package(data.package_id, organization_id)
            if not package:
                raise ValueError("Paquete no encontrado")

            # Validate vehicle type matches
            if data.vehicle_type_id and data.vehicle_type_id != package.vehicle_type_id:
                raise ValueError("El tipo de vehículo no coincide con el paquete")

            vehicle_type = package.vehicle_type

            # Get services from package
            services = [ps.service for ps in package.services if ps.service]

            # Capture package values
            captured_package_name = package.name
            captured_package_price_mxn = package.base_price_mxn
            captured_workers_required = package.workers_required
            captured_estimated_duration_minutes = package.estimated_duration_minutes
            total_duration = package.estimated_duration_minutes

        elif data.vehicle_type_id:
            # Vehicle type selected but no package
            vehicle_type = await self._get_vehicle_type(
                data.vehicle_type_id, organization_id
            )
            if not vehicle_type:
                raise ValueError("Tipo de vehículo no encontrado")

        # Legacy: manual service selection (for backwards compatibility)
        if not data.package_id and data.service_ids:
            services = await self._get_services(
                data.service_ids, location_id, organization_id
            )
            if len(services) != len(data.service_ids):
                raise ValueError("Algunos servicios no pertenecen a esta sucursal")
            total_duration = sum(s.duration_minutes for s in services)

        # Calculate ETA
        now = datetime.now(UTC)
        eta_at = now + timedelta(minutes=total_duration) if total_duration > 0 else None

        # Create ticket
        ticket = Ticket(
            organization_id=organization_id,
            location_id=location_id,
            public_code=public_code,
            plate=data.plate,
            vehicle_desc=data.vehicle_desc,
            manual_ticket_no=data.manual_ticket_no,
            customer_name=data.customer_name,
            customer_whatsapp=data.customer_whatsapp,
            current_status_id=first_status.id,
            eta_at=eta_at,
            # Package fields
            package_id=package.id if package else None,
            vehicle_type_id=vehicle_type.id if vehicle_type else None,
            captured_package_name=captured_package_name,
            captured_package_price_mxn=captured_package_price_mxn,
            captured_workers_required=captured_workers_required,
            captured_estimated_duration_minutes=captured_estimated_duration_minutes,
        )
        self.db.add(ticket)
        await self.db.flush()

        # Create service snapshots
        for idx, service in enumerate(services):
            ticket_service = TicketService(
                ticket_id=ticket.id,
                service_id=service.id,
                captured_name=service.name,
                captured_price_mxn=service.price_mxn,
                captured_duration_minutes=service.duration_minutes,
                sort_order=idx,
            )
            self.db.add(ticket_service)

        # Create "created" event
        event = TicketEvent(
            ticket_id=ticket.id,
            actor_user_id=actor.id,
            event_type=EventType.CREATED.value,
            to_status_id=first_status.id,
        )
        self.db.add(event)

        await self.db.flush()
        await self.db.refresh(ticket)

        # Trigger auto-notification for ticket_created event
        if ticket.customer_whatsapp:
            try:
                from washflow_api.services.notification import NotificationService

                notification_service = NotificationService(self.db)
                await notification_service.send_auto_notification(
                    ticket, NotificationEvent.TICKET_CREATED
                )
            except Exception as e:
                logger.warning(f"Auto-notification failed for ticket {ticket.id}: {e}")

        # Load relations
        return await self.get_ticket(ticket.id, organization_id)  # type: ignore

    async def update_ticket(
        self,
        ticket: Ticket,
        data: TicketUpdate,
        actor: User,
    ) -> Ticket:
        """Update ticket fields and optionally replace services."""
        changed_fields: dict = {}

        # Track changes for event payload
        if data.plate is not None and data.plate != ticket.plate:
            changed_fields["plate"] = {"from": ticket.plate, "to": data.plate}
            ticket.plate = data.plate

        if data.vehicle_desc is not None and data.vehicle_desc != ticket.vehicle_desc:
            changed_fields["vehicle_desc"] = {
                "from": ticket.vehicle_desc,
                "to": data.vehicle_desc,
            }
            ticket.vehicle_desc = data.vehicle_desc

        if (
            data.manual_ticket_no is not None
            and data.manual_ticket_no != ticket.manual_ticket_no
        ):
            changed_fields["manual_ticket_no"] = {
                "from": ticket.manual_ticket_no,
                "to": data.manual_ticket_no,
            }
            ticket.manual_ticket_no = data.manual_ticket_no

        if data.customer_name is not None and data.customer_name != ticket.customer_name:
            changed_fields["customer_name"] = {
                "from": ticket.customer_name,
                "to": data.customer_name,
            }
            ticket.customer_name = data.customer_name

        if (
            data.customer_whatsapp is not None
            and data.customer_whatsapp != ticket.customer_whatsapp
        ):
            changed_fields["customer_whatsapp"] = {
                "from": ticket.customer_whatsapp,
                "to": data.customer_whatsapp,
            }
            ticket.customer_whatsapp = data.customer_whatsapp

        # Replace services if provided
        if data.service_ids is not None:
            services = await self._get_services(
                data.service_ids, ticket.location_id, ticket.organization_id
            )
            if len(services) != len(data.service_ids):
                raise ValueError("Algunos servicios no pertenecen a esta sucursal")

            # Delete existing services
            for ts in ticket.services:
                await self.db.delete(ts)

            # Add new services
            for idx, service in enumerate(services):
                ticket_service = TicketService(
                    ticket_id=ticket.id,
                    service_id=service.id,
                    captured_name=service.name,
                    captured_price_mxn=service.price_mxn,
                    captured_duration_minutes=service.duration_minutes,
                    sort_order=idx,
                )
                self.db.add(ticket_service)

            changed_fields["services"] = "updated"

        # Create event if there were changes
        if changed_fields:
            event = TicketEvent(
                ticket_id=ticket.id,
                actor_user_id=actor.id,
                event_type=EventType.EDITED.value,
                payload_json=changed_fields,
            )
            self.db.add(event)

        await self.db.flush()
        await self.db.refresh(ticket)

        return await self.get_ticket(ticket.id, ticket.organization_id)  # type: ignore

    async def move_ticket(
        self,
        ticket: Ticket,
        to_status_id: str,
        actor: User,
    ) -> Ticket:
        """Move ticket to a new status."""
        # Validate the target status
        to_status = await self._get_status(
            to_status_id, ticket.location_id, ticket.organization_id
        )
        if not to_status:
            raise ValueError("Estado no encontrado en esta sucursal")

        from_status_id = ticket.current_status_id

        # Update ticket
        ticket.current_status_id = to_status_id

        # Set completed_at if moving to terminal status
        if to_status.is_terminal and not ticket.completed_at:
            ticket.completed_at = datetime.now(UTC)

        # Create move event
        event = TicketEvent(
            ticket_id=ticket.id,
            actor_user_id=actor.id,
            event_type=EventType.MOVED.value,
            from_status_id=from_status_id,
            to_status_id=to_status_id,
        )
        self.db.add(event)

        await self.db.flush()
        await self.db.refresh(ticket)

        # Trigger auto-notification for status change
        if ticket.customer_whatsapp:
            try:
                from washflow_api.services.notification import NotificationService

                notification_service = NotificationService(self.db)
                # Use DELIVERED event if terminal status, otherwise STATUS_CHANGED
                event = (
                    NotificationEvent.DELIVERED
                    if to_status.is_terminal
                    else NotificationEvent.STATUS_CHANGED
                )
                await notification_service.send_auto_notification(ticket, event)
            except Exception as e:
                logger.warning(
                    f"Auto-notification failed for ticket {ticket.id} status change: {e}"
                )

        return await self.get_ticket(ticket.id, ticket.organization_id)  # type: ignore

    async def update_eta(
        self,
        ticket: Ticket,
        eta_at: datetime | None,
        actor: User,
    ) -> Ticket:
        """Update ticket ETA manually (owner/admin only)."""
        old_eta = ticket.eta_at
        ticket.eta_at = eta_at

        # Create event
        event = TicketEvent(
            ticket_id=ticket.id,
            actor_user_id=actor.id,
            event_type=EventType.ETA_CHANGED.value,
            payload_json={
                "from": old_eta.isoformat() if old_eta else None,
                "to": eta_at.isoformat() if eta_at else None,
            },
        )
        self.db.add(event)

        await self.db.flush()
        await self.db.refresh(ticket)

        return await self.get_ticket(ticket.id, ticket.organization_id)  # type: ignore

    async def list_events(
        self,
        ticket_id: str,
        organization_id: str,
    ) -> list[TicketEvent]:
        """List all events for a ticket in chronological order."""
        result = await self.db.execute(
            select(TicketEvent)
            .join(Ticket)
            .where(
                TicketEvent.ticket_id == ticket_id,
                Ticket.organization_id == organization_id,
            )
            .options(
                selectinload(TicketEvent.actor),
                selectinload(TicketEvent.from_status),
                selectinload(TicketEvent.to_status),
            )
            .order_by(TicketEvent.happened_at.asc())
        )
        return list(result.scalars().all())

    async def _get_first_status(
        self,
        location_id: str,
        organization_id: str,
    ) -> Status | None:
        """Get the first status by sort_order for a location."""
        result = await self.db.execute(
            select(Status)
            .where(
                Status.location_id == location_id,
                Status.organization_id == organization_id,
            )
            .order_by(Status.sort_order)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_status(
        self,
        status_id: str,
        location_id: str,
        organization_id: str,
    ) -> Status | None:
        """Get a status ensuring it belongs to the location."""
        result = await self.db.execute(
            select(Status).where(
                Status.id == status_id,
                Status.location_id == location_id,
                Status.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_services(
        self,
        service_ids: list[str],
        location_id: str,
        organization_id: str,
    ) -> list[Service]:
        """Get services by IDs, ensuring they belong to the location."""
        if not service_ids:
            return []

        result = await self.db.execute(
            select(Service).where(
                Service.id.in_(service_ids),
                Service.location_id == location_id,
                Service.organization_id == organization_id,
                Service.active == True,  # noqa: E712
            )
        )
        services = list(result.scalars().all())

        # Return in the order of service_ids
        service_map = {s.id: s for s in services}
        return [service_map[sid] for sid in service_ids if sid in service_map]

    async def _generate_unique_public_code(
        self,
        organization_id: str,
        max_attempts: int = 10,
    ) -> str:
        """Generate a unique public code within the organization."""
        for _ in range(max_attempts):
            code = generate_public_code()
            # Check if exists
            result = await self.db.execute(
                select(func.count()).where(
                    Ticket.organization_id == organization_id,
                    Ticket.public_code == code,
                )
            )
            if result.scalar() == 0:
                return code

        # Fallback: add timestamp suffix
        code = generate_public_code()
        suffix = hex(int(datetime.now(UTC).timestamp()))[2:][-3:].upper()
        return f"{code}{suffix}"

    async def _get_package(
        self,
        package_id: str,
        organization_id: str,
    ) -> Package | None:
        """Get a package with services loaded."""
        result = await self.db.execute(
            select(Package)
            .where(
                Package.id == package_id,
                Package.organization_id == organization_id,
                Package.is_active == True,  # noqa: E712
            )
            .options(
                selectinload(Package.vehicle_type),
                selectinload(Package.services).selectinload(PackageService.service),
            )
        )
        return result.scalar_one_or_none()

    async def _get_vehicle_type(
        self,
        vehicle_type_id: str,
        organization_id: str,
    ) -> VehicleType | None:
        """Get a vehicle type by ID."""
        result = await self.db.execute(
            select(VehicleType).where(
                VehicleType.id == vehicle_type_id,
                VehicleType.organization_id == organization_id,
                VehicleType.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()
