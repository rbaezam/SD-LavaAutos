"""Pytest configuration and fixtures."""

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from washflow_api.db.base import Base
from washflow_api.db.session import get_db
from washflow_api.main import app
from washflow_api.models import Location, Organization, Status, User, UserRole
from washflow_api.core.security import hash_password, create_access_token


# Use PostgreSQL for tests (via docker-compose.test.yml)
# Run: cd infra && docker compose -f docker-compose.test.yml up -d
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://washflow_test:washflow_test@localhost:5434/washflow_test",
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session-scoped fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    """Create a test database engine with PostgreSQL."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        # Drop all tables first for clean state
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with test database."""

    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_org(db_session: AsyncSession) -> Organization:
    """Create a test organization."""
    org = Organization(name="Test Org")
    db_session.add(org)
    await db_session.flush()
    await db_session.refresh(org)
    return org


@pytest.fixture
async def test_location(db_session: AsyncSession, test_org: Organization) -> Location:
    """Create a test location."""
    location = Location(
        organization_id=test_org.id,
        name="Test Location",
    )
    db_session.add(location)
    await db_session.flush()
    await db_session.refresh(location)
    return location


@pytest.fixture
async def test_statuses(
    db_session: AsyncSession, test_org: Organization, test_location: Location
) -> list[Status]:
    """Create default test statuses."""
    statuses_data = [
        {"name": "En espera", "sort_order": 0, "is_terminal": False},
        {"name": "En lavado", "sort_order": 1, "is_terminal": False},
        {"name": "Entregado", "sort_order": 2, "is_terminal": True},
    ]
    statuses = []
    for data in statuses_data:
        status = Status(
            organization_id=test_org.id,
            location_id=test_location.id,
            **data,
        )
        db_session.add(status)
        statuses.append(status)
    await db_session.flush()
    for s in statuses:
        await db_session.refresh(s)
    return statuses


@pytest.fixture
async def test_owner(
    db_session: AsyncSession, test_org: Organization, test_location: Location
) -> User:
    """Create a test owner user."""
    user = User(
        email="owner@test.com",
        hashed_password=hash_password("password123"),
        full_name="Test Owner",
        organization_id=test_org.id,
        location_id=test_location.id,
        role=UserRole.OWNER.value,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_staff(
    db_session: AsyncSession, test_org: Organization, test_location: Location
) -> User:
    """Create a test staff user."""
    user = User(
        email="staff@test.com",
        hashed_password=hash_password("password123"),
        full_name="Test Staff",
        organization_id=test_org.id,
        location_id=test_location.id,
        role=UserRole.STAFF.value,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest.fixture
def owner_token(test_owner: User) -> str:
    """Create an access token for the owner user."""
    return create_access_token(test_owner.id)


@pytest.fixture
def staff_token(test_staff: User) -> str:
    """Create an access token for the staff user."""
    return create_access_token(test_staff.id)


@pytest.fixture
def owner_headers(owner_token: str) -> dict[str, str]:
    """Create authorization headers for owner."""
    return {"Authorization": f"Bearer {owner_token}"}


@pytest.fixture
def staff_headers(staff_token: str) -> dict[str, str]:
    """Create authorization headers for staff."""
    return {"Authorization": f"Bearer {staff_token}"}
