"""
Integration tests for UserRepository using a real PostgreSQL database with testcontainers.

This test suite:
1. Starts a PostgreSQL container using testcontainers
2. Applies database migrations to create the necessary tables
3. Tests all CRUD operations against the real database
4. Verifies data persistence and retrieval
"""

import asyncio
import time
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from kink import di
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer

from sso_anythingllm_entity.user import User
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError
from sso_anythingllm_repository.user_repository import UserRepository

# Migration configuration
MIGRATIONS_PATH = Path(__file__).parents[1] / "migrations"
ALEMBIC_INI_PATH = Path(__file__).parents[3] / "alembic.ini"


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def postgres_container(event_loop) -> AsyncGenerator[PostgresContainer, None]:
    """Start and configure PostgreSQL container for integration tests."""
    # Start PostgreSQL container
    postgres_container = PostgresContainer("postgres:15").with_bind_ports(5432)
    postgres_container.start()

    # Wait for container to be ready
    time.sleep(3)
    postgres_container._connect()

    print(f"PostgreSQL container started: {postgres_container.get_connection_url()}")

    yield postgres_container

    # Cleanup
    postgres_container.stop()


@pytest_asyncio.fixture(scope="session")
async def test_db_config(postgres_container) -> AsyncGenerator[AsyncPostgresConf, None]:
    """Create database configuration and apply migrations."""
    # Create AsyncPostgresConf with container connection details
    postgres_conf = AsyncPostgresConf(
        host=postgres_container.get_container_host_ip(),
        port=int(postgres_container.get_exposed_port(5432)),
        username=postgres_container.username,
        password=postgres_container.password,
        database=postgres_container.dbname,
    )

    # Store in DI container
    di[AsyncPostgresConf] = postgres_conf

    # Apply migrations
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option("script_location", str(MIGRATIONS_PATH))
    alembic_cfg.set_main_option("sqlalchemy.url", postgres_container.get_connection_url())

    print("Applying database migrations...")
    command.upgrade(alembic_cfg, "head")

    # Verify migrations were applied
    engine = postgres_conf.sync_engine
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename='anythingllm_user';"))
        assert result.first() is not None, "User table should exist after migrations"
        print("✅ Migrations applied successfully")

    yield postgres_conf

    # Cleanup
    di[AsyncPostgresConf] = None


@pytest_asyncio.fixture
async def user_repository(test_db_config) -> AsyncGenerator[UserRepository, None]:
    """Create UserRepository instance with real database configuration."""
    repository = UserRepository(test_db_config)
    yield repository


@pytest_asyncio.fixture
async def clean_database(user_repository) -> AsyncGenerator[None, None]:
    """Clean the database before each test to ensure isolation."""
    # Clean up any existing users
    try:
        all_users = await user_repository.get_all_users()
        for user in all_users:
            await user_repository.delete_by_keycloak_id(user.keycloak_id)
    except Exception:
        # Ignore errors during cleanup
        pass

    yield

    # Clean up after test as well
    try:
        all_users = await user_repository.get_all_users()
        for user in all_users:
            await user_repository.delete_by_keycloak_id(user.keycloak_id)
    except Exception:
        # Ignore errors during cleanup
        pass


@pytest.fixture
def sample_users():
    """Create sample users for testing."""
    return [
        User(keycloak_id="user-001", internal_id=1, name="John Doe", role="admin"),
        User(keycloak_id="user-002", internal_id=2, name="Jane Smith", role="manager"),
        User(keycloak_id="user-003", internal_id=3, name="Bob Wilson", role="default"),
        User(keycloak_id="user-004", internal_id=4, name="Alice Brown", role="admin"),
    ]


class TestUserRepositoryIntegration:
    """Integration tests for UserRepository using real PostgreSQL database."""

    @pytest.mark.asyncio
    async def test_save_user_success(self, user_repository, clean_database, sample_users):
        """Test successful user creation."""
        user = sample_users[0]

        # Create user
        created_user = await user_repository.save(user)

        # Verify user was created
        assert created_user.keycloak_id == user.keycloak_id
        assert created_user.name == user.name
        assert created_user.role == user.role
        assert created_user.internal_id == user.internal_id

    @pytest.mark.asyncio
    async def test_save_user_already_exists(self, user_repository, clean_database, sample_users):
        """Test user creation when user already exists."""
        user = sample_users[0]

        # Create user first time
        await user_repository.save(user)

        # Try to create same user again
        with pytest.raises(ValidationError, match="already exists"):
            await user_repository.save(user)

    @pytest.mark.asyncio
    async def test_get_by_keycloak_id_success(self, user_repository, clean_database, sample_users):
        """Test successful user retrieval by keycloak_id."""
        user = sample_users[1]

        # Create user
        await user_repository.save(user)

        # Retrieve user
        retrieved_user = await user_repository.get_by_keycloak_id(user.keycloak_id)

        # Verify retrieved user
        assert retrieved_user.keycloak_id == user.keycloak_id
        assert retrieved_user.name == user.name
        assert retrieved_user.role == user.role
        assert retrieved_user.internal_id == user.internal_id

    @pytest.mark.asyncio
    async def test_get_by_keycloak_id_not_found(self, user_repository, clean_database):
        """Test user retrieval when user doesn't exist."""
        with pytest.raises(ValidationError, match="not found"):
            await user_repository.get_by_keycloak_id("non-existent-user")

    @pytest.mark.asyncio
    async def test_get_by_anythingllm_id_success(self, user_repository, clean_database, sample_users):
        """Test successful user retrieval by internal_id."""
        user = sample_users[2]

        # Create user
        await user_repository.save(user)

        # Retrieve user by internal_id
        retrieved_user = await user_repository.get_by_anythingllm_id(user.internal_id)

        # Verify retrieved user
        assert retrieved_user.keycloak_id == user.keycloak_id
        assert retrieved_user.name == user.name
        assert retrieved_user.role == user.role
        assert retrieved_user.internal_id == user.internal_id

    @pytest.mark.asyncio
    async def test_get_by_anythingllm_id_not_found(self, user_repository, clean_database):
        """Test user retrieval by internal_id when user doesn't exist."""
        with pytest.raises(ValidationError, match="not found"):
            await user_repository.get_by_anythingllm_id(99999)

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_repository, clean_database, sample_users):
        """Test successful user update."""
        user = sample_users[3]

        # Create user
        await user_repository.save(user)

        # Update user
        updated_user = User(
            keycloak_id=user.keycloak_id, internal_id=user.internal_id, name="Updated Alice Brown", role="manager"
        )

        result = await user_repository.update(updated_user)

        # Verify user was updated
        assert result.name == "Updated Alice Brown"
        assert result.role == "manager"
        assert result.keycloak_id == user.keycloak_id
        assert result.internal_id == user.internal_id

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_repository, clean_database, sample_users):
        """Test user update when user doesn't exist."""
        user = sample_users[0]
        user.keycloak_id = "non-existent-user"

        with pytest.raises(ValidationError, match="not found"):
            await user_repository.update(user)

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_repository, clean_database, sample_users):
        """Test successful user deletion."""
        user = sample_users[0]

        # Create user
        await user_repository.save(user)

        # Verify user exists
        retrieved_user = await user_repository.get_by_keycloak_id(user.keycloak_id)
        assert retrieved_user is not None

        # Delete user
        await user_repository.delete_by_keycloak_id(user.keycloak_id)

        # Verify user was deleted
        with pytest.raises(ValidationError, match="not found"):
            await user_repository.get_by_keycloak_id(user.keycloak_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_repository, clean_database):
        """Test user deletion when user doesn't exist."""
        with pytest.raises(ValidationError, match="not found"):
            await user_repository.delete_by_keycloak_id("non-existent-user")

    @pytest.mark.asyncio
    async def test_get_all_users(self, user_repository, clean_database, sample_users):
        """Test retrieving all users."""
        # Create multiple users
        for user in sample_users:
            await user_repository.save(user)

        # Retrieve all users
        retrieved_users = await user_repository.get_all_users()

        # Verify all users were retrieved
        assert len(retrieved_users) == len(sample_users)

        # Verify each user exists
        for expected_user in sample_users:
            found = any(u.keycloak_id == expected_user.keycloak_id for u in retrieved_users)
            assert found, f"User {expected_user.keycloak_id} should be in retrieved users"

    @pytest.mark.asyncio
    async def test_get_users_by_role(self, user_repository, clean_database, sample_users):
        """Test retrieving users by role."""
        # Create users with different roles
        for user in sample_users:
            await user_repository.save(user)

        # Get admin users
        admin_users = await user_repository.get_users_by_role("admin")
        assert len(admin_users) == 2  # user-001 and user-004 are admins

        # Get manager users
        manager_users = await user_repository.get_users_by_role("manager")
        assert len(manager_users) == 1  # user-002 is manager

        # Get default users
        default_users = await user_repository.get_users_by_role("default")
        assert len(default_users) == 1  # user-003 is default

    @pytest.mark.asyncio
    async def test_user_exists(self, user_repository, clean_database, sample_users):
        """Test user existence check."""
        user = sample_users[0]

        # Check user doesn't exist initially
        exists = await user_repository.user_exists(user.keycloak_id)
        assert exists is False

        # Create user
        await user_repository.save(user)

        # Check user exists now
        exists = await user_repository.user_exists(user.keycloak_id)
        assert exists is True

    @pytest.mark.asyncio
    async def test_count_users(self, user_repository, clean_database, sample_users):
        """Test user counting."""
        # Count should be 0 initially
        count = await user_repository.count_users()
        assert count == 0

        # Create users
        for user in sample_users:
            await user_repository.save(user)

        # Count should match number of created users
        count = await user_repository.count_users()
        assert count == len(sample_users)

    @pytest.mark.asyncio
    async def test_comprehensive_crud_workflow(self, user_repository, clean_database, sample_users):
        """Test a comprehensive CRUD workflow with multiple operations."""
        # 1. Create users
        created_users = []
        for user in sample_users:
            created_user = await user_repository.save(user)
            created_users.append(created_user)

        # 2. Verify all users were created
        all_users = await user_repository.get_all_users()
        assert len(all_users) == len(sample_users)

        # 3. Update a user
        user_to_update = created_users[0]
        updated_user = User(
            keycloak_id=user_to_update.keycloak_id,
            internal_id=user_to_update.internal_id,
            name="Completely Updated Name",
            role="default",
        )
        updated_result = await user_repository.update(updated_user)
        assert updated_result.name == "Completely Updated Name"
        assert updated_result.role == "default"

        # 4. Verify update persisted
        retrieved_user = await user_repository.get_by_keycloak_id(user_to_update.keycloak_id)
        assert retrieved_user.name == "Completely Updated Name"
        assert retrieved_user.role == "default"

        # 5. Delete a user
        user_to_delete = created_users[1]
        await user_repository.delete_by_keycloak_id(user_to_delete.keycloak_id)

        # 6. Verify user was deleted
        with pytest.raises(ValidationError, match="not found"):
            await user_repository.get_by_keycloak_id(user_to_delete.keycloak_id)

        # 7. Verify count decreased
        final_count = await user_repository.count_users()
        assert final_count == len(sample_users) - 1

        # 8. Verify user doesn't exist
        exists = await user_repository.user_exists(user_to_delete.keycloak_id)
        assert exists is False
