import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio

# Core libraries
from kink import di
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from testcontainers.postgres import PostgresContainer

# Source imports
from sso_anythingllm_repository.config import AsyncPostgresConf


# Event loop fixture - MUST be defined at session scope
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# Combined fixture for creating DB container and tables
@pytest_asyncio.fixture(scope="session")
async def test_db(event_loop) -> AsyncGenerator[AsyncPostgresConf, None]:
    """
    Set up a test PostgreSQL container and create all tables.
    """
    # Start and configure PostgreSQL container
    postgres_container = PostgresContainer("postgres:14").with_bind_ports(5432)
    postgres_container.start()

    # Wait for container to be ready
    postgres_container._connect()

    # Create AsyncPostgresConf with container connection details
    dsn = postgres_container.get_connection_url(driver="asyncpg")
    print(f"Connection URL: {dsn}")

    postgres_conf = AsyncPostgresConf(
        host=postgres_container.get_container_host_ip(),
        port=int(postgres_container.get_exposed_port(5432)),
        username=postgres_container.username,
        password=postgres_container.password,
        database=postgres_container.dbname,
    )

    # Create async engine
    engine = postgres_conf.engine

    # First ensure tables don't exist
    async with engine.begin() as connection:
        await connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        await connection.execute(text("CREATE SCHEMA public"))
        await connection.commit()

    # Create all tables
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    # Verify creation worked
    async with engine.connect() as connection:
        result = await connection.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"Created tables: {tables}")

    # Return configuration for other fixtures to use
    di[AsyncPostgresConf] = postgres_conf
    yield postgres_conf

    # Cleanup
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()
    postgres_container.stop()
    di[AsyncPostgresConf] = None


# Create a shared async engine at session scope
@pytest.fixture(scope="session")
def async_engine(test_db, event_loop):
    """Create a shared async engine using the session-scoped event loop."""
    engine = create_async_engine(
        test_db.url,
        future=True,
    )
    yield engine

    # Close engine when test session ends
    async def close_engine():
        await engine.dispose()

    event_loop.run_until_complete(close_engine())


# Fixture for AsyncSession
@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create an async session for testing.
    """
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        # Rollback any changes after the test
        await session.rollback()


@pytest.fixture
def postgres_dsn(test_db: AsyncPostgresConf) -> str:
    """
    Return the PostgreSQL DSN string for the test database.
    This is needed for tests that need direct access to the DSN.
    """
    return test_db.url.render_as_string(hide_password=False)
