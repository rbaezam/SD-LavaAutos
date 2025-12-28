"""Authentication service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from washflow_api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from washflow_api.models import Location, Organization, Status, User, UserRole
from washflow_api.schemas.auth import RegisterRequest, TokenResponse

# Default statuses to seed when creating a new location
DEFAULT_STATUSES = [
    {"name": "En espera", "sort_order": 0, "is_terminal": False},
    {"name": "En lavado", "sort_order": 1, "is_terminal": False},
    {"name": "En secado", "sort_order": 2, "is_terminal": False},
    {"name": "Detallado", "sort_order": 3, "is_terminal": False},
    {"name": "Listo", "sort_order": 4, "is_terminal": False},
    {"name": "Entregado", "sort_order": 5, "is_terminal": True},
]


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        """Register a new user with default organization and location."""
        # Check if user exists
        existing = await self.get_user_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        # Create organization for the new user
        org_name = data.full_name or data.email.split("@")[0]
        organization = Organization(name=f"Org de {org_name}")
        self.db.add(organization)
        await self.db.flush()

        # Create default location
        location = Location(
            organization_id=organization.id,
            name="Sucursal Principal",
        )
        self.db.add(location)
        await self.db.flush()

        # Seed default statuses for the location
        for status_data in DEFAULT_STATUSES:
            status = Status(
                organization_id=organization.id,
                location_id=location.id,
                name=status_data["name"],
                sort_order=status_data["sort_order"],
                is_terminal=status_data["is_terminal"],
            )
            self.db.add(status)
        await self.db.flush()

        # Create user as owner of the new organization
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            organization_id=organization.id,
            location_id=location.id,
            role=UserRole.OWNER.value,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by ID with organization and location loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.organization),
                selectinload(User.location),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    def create_tokens(user_id: str) -> TokenResponse:
        """Create access and refresh tokens for a user."""
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse | None:
        """Refresh tokens using a valid refresh token."""
        payload = decode_token(refresh_token)
        if not payload:
            return None
        if payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        user = await self.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None

        return self.create_tokens(user_id)
