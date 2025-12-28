"""API dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from washflow_api.core.security import decode_token
from washflow_api.db import get_db
from washflow_api.models.user import User, UserRole
from washflow_api.services.auth import AuthService

# HTTP Bearer scheme for JWT tokens
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Dependency that returns the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_exception

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """
    Factory for creating a dependency that requires specific roles.

    Usage:
        @router.post("/locations", dependencies=[Depends(require_roles(UserRole.OWNER, UserRole.ADMIN))])
        async def create_location(...):
            ...
    """

    async def check_roles(current_user: CurrentUser) -> User:
        role_values = [r.value for r in roles]
        if current_user.role not in role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return check_roles


def require_manager():
    """Require user to be owner or admin."""
    return require_roles(UserRole.OWNER, UserRole.ADMIN)


# Type alias for manager user
ManagerUser = Annotated[User, Depends(require_manager())]
