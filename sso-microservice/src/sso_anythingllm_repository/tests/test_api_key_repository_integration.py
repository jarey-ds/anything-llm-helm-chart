"""
Integration tests for ApiKeyRepository using a real PostgreSQL database with testcontainers.

This test suite:
1. Starts a PostgreSQL container using testcontainers
2. Applies database migrations to create the necessary tables
3. Tests all CRUD operations against the real database
4. Verifies data persistence and retrieval
"""

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

from sso_anythingllm_entity.api_key import ApiKey
from sso_anythingllm_repository.api_key_repository import ApiKeyRepository
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError

# Migration configuration
MIGRATIONS_PATH = Path(__file__).parents[1] / "migrations"
ALEMBIC_INI_PATH = Path(__file__).parents[3] / "alembic.ini"


@pytest_asyncio.fixture(scope="session")
async def postgres_container() -> AsyncGenerator[PostgresContainer, None]:
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
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename='api_key';"))
        assert result.first() is not None, "User table should exist after migrations"
        print("✅ Migrations applied successfully")

    yield postgres_conf

    # Cleanup
    di[AsyncPostgresConf] = None


@pytest_asyncio.fixture
async def api_key_repository(test_db_config) -> AsyncGenerator[ApiKeyRepository, None]:
    """Create ApiKeyRepository instance with real database configuration."""
    repository = ApiKeyRepository(test_db_config)
    yield repository


@pytest_asyncio.fixture
async def clean_database(api_key_repository) -> AsyncGenerator[None, None]:
    """Clean the database before each test to ensure isolation."""
    # Clean up any existing API keys
    try:
        all_api_keys = await api_key_repository.get_all_api_keys()
        for api_key in all_api_keys:
            await api_key_repository.delete_by_value(api_key.value)
    except Exception:
        # Ignore errors during cleanup
        pass

    yield

    # Clean up after test as well
    try:
        all_api_keys = await api_key_repository.get_all_api_keys()
        for api_key in all_api_keys:
            await api_key_repository.delete_by_value(api_key.value)
    except Exception:
        # Ignore errors during cleanup
        pass


class TestApiKeyRepositoryIntegration:
    """Integration tests for ApiKeyRepository using real PostgreSQL database."""

    @pytest.mark.asyncio
    async def test_save_api_key_success(self, api_key_repository, clean_database):
        """Test successful API key creation."""
        # Create API key
        api_key = ApiKey(value="test-api-key-123")

        # Save API key
        saved_api_key = await api_key_repository.save(api_key)

        # Assertions
        assert saved_api_key.value == "test-api-key-123"

        # Verify it was saved by retrieving it
        retrieved_api_key = await api_key_repository.get_by_value("test-api-key-123")
        assert retrieved_api_key.value == "test-api-key-123"

    @pytest.mark.asyncio
    async def test_save_api_key_already_exists(self, api_key_repository, clean_database):
        """Test API key creation when API key already exists."""
        # Create and save first API key
        api_key1 = ApiKey(value="test-api-key-123")
        await api_key_repository.save(api_key1)

        # Try to save another API key with the same value
        api_key2 = ApiKey(value="test-api-key-123")

        # Should raise ValidationError
        with pytest.raises(ValidationError, match="already exists"):
            await api_key_repository.save(api_key2)

    @pytest.mark.asyncio
    async def test_get_by_value_success(self, api_key_repository, clean_database):
        """Test successful API key retrieval by value."""
        # Create and save API key
        api_key = ApiKey(value="test-api-key-123")
        await api_key_repository.save(api_key)

        # Retrieve API key
        retrieved_api_key = await api_key_repository.get_by_value("test-api-key-123")

        # Assertions
        assert retrieved_api_key.value == "test-api-key-123"

    @pytest.mark.asyncio
    async def test_get_by_value_not_found(self, api_key_repository, clean_database):
        """Test API key retrieval when API key doesn't exist."""
        # Try to retrieve non-existent API key
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.get_by_value("non-existent-api-key")

    @pytest.mark.asyncio
    async def test_update_api_key_success(self, api_key_repository, clean_database):
        """Test successful API key update."""
        # Create and save API key
        api_key = ApiKey(value="test-api-key-123")
        saved_api_key = await api_key_repository.save(api_key)

        # Update API key (in this case, ApiKey only has one field, so we'll just verify it exists)
        updated_api_key = await api_key_repository.update(saved_api_key)

        # Assertions
        assert updated_api_key.value == "test-api-key-123"

        # Verify it still exists in database
        retrieved_api_key = await api_key_repository.get_by_value("test-api-key-123")
        assert retrieved_api_key.value == "test-api-key-123"

    @pytest.mark.asyncio
    async def test_update_api_key_not_found(self, api_key_repository, clean_database):
        """Test API key update when API key doesn't exist."""
        # Try to update non-existent API key
        api_key = ApiKey(value="non-existent-api-key")

        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.update(api_key)

    @pytest.mark.asyncio
    async def test_delete_api_key_success(self, api_key_repository, clean_database):
        """Test successful API key deletion."""
        # Create and save API key
        api_key = ApiKey(value="test-api-key-123")
        await api_key_repository.save(api_key)

        # Verify it exists
        assert await api_key_repository.api_key_exists("test-api-key-123")

        # Delete API key
        await api_key_repository.delete_by_value("test-api-key-123")

        # Verify it was deleted
        assert not await api_key_repository.api_key_exists("test-api-key-123")

        # Try to retrieve it should fail
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.get_by_value("test-api-key-123")

    @pytest.mark.asyncio
    async def test_delete_api_key_not_found(self, api_key_repository, clean_database):
        """Test API key deletion when API key doesn't exist."""
        # Try to delete non-existent API key
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.delete_by_value("non-existent-api-key")

    @pytest.mark.asyncio
    async def test_get_all_api_keys(self, api_key_repository, clean_database):
        """Test retrieving all API keys."""
        # Create and save multiple API keys
        api_key1 = ApiKey(value="test-api-key-1")
        api_key2 = ApiKey(value="test-api-key-2")
        api_key3 = ApiKey(value="test-api-key-3")

        await api_key_repository.save(api_key1)
        await api_key_repository.save(api_key2)
        await api_key_repository.save(api_key3)

        # Retrieve all API keys
        all_api_keys = await api_key_repository.get_all_api_keys()

        # Assertions
        assert len(all_api_keys) == 3
        api_key_values = [api_key.value for api_key in all_api_keys]
        assert "test-api-key-1" in api_key_values
        assert "test-api-key-2" in api_key_values
        assert "test-api-key-3" in api_key_values

    @pytest.mark.asyncio
    async def test_api_key_exists_true(self, api_key_repository, clean_database):
        """Test api_key_exists when API key exists."""
        # Create and save API key
        api_key = ApiKey(value="test-api-key-123")
        await api_key_repository.save(api_key)

        # Check if it exists
        exists = await api_key_repository.api_key_exists("test-api-key-123")

        # Assertions
        assert exists is True

    @pytest.mark.asyncio
    async def test_api_key_exists_false(self, api_key_repository, clean_database):
        """Test api_key_exists when API key doesn't exist."""
        # Check if non-existent API key exists
        exists = await api_key_repository.api_key_exists("non-existent-api-key")

        # Assertions
        assert exists is False

    @pytest.mark.asyncio
    async def test_count_api_keys(self, api_key_repository, clean_database):
        """Test counting API keys."""
        # Initially should be 0
        count = await api_key_repository.count_api_keys()
        assert count == 0

        # Create and save API keys
        api_key1 = ApiKey(value="test-api-key-1")
        api_key2 = ApiKey(value="test-api-key-2")

        await api_key_repository.save(api_key1)
        count = await api_key_repository.count_api_keys()
        assert count == 1

        await api_key_repository.save(api_key2)
        count = await api_key_repository.count_api_keys()
        assert count == 2

    @pytest.mark.asyncio
    async def test_legacy_create_method(self, api_key_repository, clean_database):
        """Test legacy create method."""
        # Create API key using legacy method
        api_key = ApiKey(value="test-api-key-123")
        created_api_key = await api_key_repository.create(api_key)

        # Assertions
        assert created_api_key.value == "test-api-key-123"

        # Verify it was saved
        retrieved_api_key = await api_key_repository.get_by_value("test-api-key-123")
        assert retrieved_api_key.value == "test-api-key-123"

    @pytest.mark.asyncio
    async def test_legacy_delete_method(self, api_key_repository, clean_database):
        """Test legacy delete method."""
        # Create and save API key
        api_key = ApiKey(value="test-api-key-123")
        await api_key_repository.save(api_key)

        # Delete using legacy method
        await api_key_repository.delete(api_key)

        # Verify it was deleted
        assert not await api_key_repository.api_key_exists("test-api-key-123")

    @pytest.mark.asyncio
    async def test_legacy_get_api_keys_method(self, api_key_repository, clean_database):
        """Test legacy get_api_keys method."""
        # Create and save API keys
        api_key1 = ApiKey(value="test-api-key-1")
        api_key2 = ApiKey(value="test-api-key-2")

        await api_key_repository.save(api_key1)
        await api_key_repository.save(api_key2)

        # Retrieve using legacy method
        api_keys = await api_key_repository.get_api_keys()

        # Assertions
        assert len(api_keys) == 2
        api_key_values = [api_key.value for api_key in api_keys]
        assert "test-api-key-1" in api_key_values
        assert "test-api-key-2" in api_key_values

    @pytest.mark.asyncio
    async def test_comprehensive_crud_workflow(self, api_key_repository, clean_database):
        """Test comprehensive CRUD workflow."""
        # 1. CREATE - Save multiple API keys
        api_key1 = ApiKey(value="workflow-api-key-1")
        api_key2 = ApiKey(value="workflow-api-key-2")
        api_key3 = ApiKey(value="workflow-api-key-3")

        saved_api_key1 = await api_key_repository.save(api_key1)
        saved_api_key2 = await api_key_repository.save(api_key2)
        saved_api_key3 = await api_key_repository.save(api_key3)

        # 2. READ - Verify all API keys were saved
        assert await api_key_repository.count_api_keys() == 3
        assert await api_key_repository.api_key_exists("workflow-api-key-1")
        assert await api_key_repository.api_key_exists("workflow-api-key-2")
        assert await api_key_repository.api_key_exists("workflow-api-key-3")

        # 3. READ - Get individual API keys
        retrieved_api_key1 = await api_key_repository.get_by_value("workflow-api-key-1")
        retrieved_api_key2 = await api_key_repository.get_by_value("workflow-api-key-2")
        retrieved_api_key3 = await api_key_repository.get_by_value("workflow-api-key-3")

        assert retrieved_api_key1.value == "workflow-api-key-1"
        assert retrieved_api_key2.value == "workflow-api-key-2"
        assert retrieved_api_key3.value == "workflow-api-key-3"

        # 4. READ - Get all API keys
        all_api_keys = await api_key_repository.get_all_api_keys()
        assert len(all_api_keys) == 3

        # 5. UPDATE - Update API keys (in this case, just verify they exist)
        updated_api_key1 = await api_key_repository.update(saved_api_key1)
        updated_api_key2 = await api_key_repository.update(saved_api_key2)
        updated_api_key3 = await api_key_repository.update(saved_api_key3)

        assert updated_api_key1.value == "workflow-api-key-1"
        assert updated_api_key2.value == "workflow-api-key-2"
        assert updated_api_key3.value == "workflow-api-key-3"

        # 6. DELETE - Delete API keys
        await api_key_repository.delete_by_value("workflow-api-key-1")
        await api_key_repository.delete_by_value("workflow-api-key-2")
        await api_key_repository.delete_by_value("workflow-api-key-3")

        # 7. VERIFY - Verify all API keys were deleted
        assert await api_key_repository.count_api_keys() == 0
        assert not await api_key_repository.api_key_exists("workflow-api-key-1")
        assert not await api_key_repository.api_key_exists("workflow-api-key-2")
        assert not await api_key_repository.api_key_exists("workflow-api-key-3")

        # 8. VERIFY - Try to retrieve deleted API keys should fail
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.get_by_value("workflow-api-key-1")
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.get_by_value("workflow-api-key-2")
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.get_by_value("workflow-api-key-3")
