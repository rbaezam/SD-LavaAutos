"""Pydantic schemas for API request/response validation."""

from washflow_api.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from washflow_api.schemas.location import (
    LocationCreate,
    LocationListResponse,
    LocationOut,
    LocationUpdate,
)
from washflow_api.schemas.organization import (
    OrgMeResponse,
    OrganizationOut,
    OrganizationWithRole,
)
from washflow_api.schemas.service import (
    ServiceCreate,
    ServiceListResponse,
    ServiceOut,
    ServiceUpdate,
)
from washflow_api.schemas.status import (
    StatusCreate,
    StatusListResponse,
    StatusOut,
    StatusReorderRequest,
    StatusUpdate,
)
from washflow_api.schemas.ticket import (
    EtaUpdateRequest,
    TicketCreate,
    TicketEventListResponse,
    TicketEventOut,
    TicketListItem,
    TicketListResponse,
    TicketMoveRequest,
    TicketOut,
    TicketServiceSnapshot,
    TicketUpdate,
)

__all__ = [
    # Auth
    "LoginRequest",
    "RefreshRequest",
    "RegisterRequest",
    "TokenResponse",
    "UserResponse",
    # Organization
    "OrgMeResponse",
    "OrganizationOut",
    "OrganizationWithRole",
    # Location
    "LocationCreate",
    "LocationListResponse",
    "LocationOut",
    "LocationUpdate",
    # Service
    "ServiceCreate",
    "ServiceListResponse",
    "ServiceOut",
    "ServiceUpdate",
    # Status
    "StatusCreate",
    "StatusListResponse",
    "StatusOut",
    "StatusReorderRequest",
    "StatusUpdate",
    # Ticket
    "EtaUpdateRequest",
    "TicketCreate",
    "TicketEventListResponse",
    "TicketEventOut",
    "TicketListItem",
    "TicketListResponse",
    "TicketMoveRequest",
    "TicketOut",
    "TicketServiceSnapshot",
    "TicketUpdate",
]
