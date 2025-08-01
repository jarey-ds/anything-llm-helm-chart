import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from artemis_model_catalogue_dto.model import ModelInstanceDto
from artemis_model_catalogue_dto_entity_mapper.model import ModelInstanceDTOEntityMapper

# Source imports
from artemis_model_catalogue_entity.model import (
    Capability,
    ModelInstance,
    ModelPropertyInstance,
    ModelPropertyTemplate,
    ModelPropertyType,
    ModelTemplate,
    ModelTemplateCapability,
    ModelType,
)

# Import all models to ensure their metadata is registered
from artemis_model_catalogue_entity.provider import (
    OwnerType,
    ProviderInstance,
    ProviderModel,
    ProviderPropertyInstance,
    ProviderPropertyTemplate,
    ProviderPropertyType,
    ProviderTemplate,
)
from artemis_model_catalogue_repository.config import AsyncPostgresConf
from artemis_model_catalogue_repository.model_instance_repository import ModelInstanceRepository
from artemis_model_catalogue_repository.model_template_repository import ModelTemplateRepository
from artemis_model_catalogue_repository.model_type_repository import ModelTypeRepository
from artemis_model_catalogue_repository.provider_instance_repository import ProviderInstanceRepository
from artemis_model_catalogue_repository.provider_model_repository import ProviderModelRepository
from artemis_model_catalogue_repository.provider_template_repository import ProviderTemplateRepository
from core_mapping.mapper_manager import mapper_manager
from core_persistence.datasource.connector import AsyncConnector

# Core libraries
from core_persistence_sqlalchemy.async_provider.connector import AsyncSqlConnector
from kink import di
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from testcontainers.postgres import PostgresContainer


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


@pytest_asyncio.fixture
async def sql_connector(test_db: AsyncPostgresConf) -> AsyncGenerator[AsyncSqlConnector, None]:
    """
    Live SqlConnector backed by the test database.
    """
    dsn = test_db.url.render_as_string(hide_password=False)
    print(f"Using DSN: {dsn}")
    connector = AsyncSqlConnector(dsn=dsn)
    await connector.connect()
    di[AsyncConnector] = connector
    yield connector
    await connector.close()
    di[AsyncSqlConnector] = None


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


# Fixture for ProviderTemplateRepository based on test_db
@pytest_asyncio.fixture
async def provider_template_repository(
    sql_connector: AsyncSqlConnector,
) -> ProviderTemplateRepository:
    """
    Create a ProviderTemplateRepository using the test database.
    """
    return ProviderTemplateRepository(sql_connector)


# Fixture for ProviderTemplateRepository based on test_db
@pytest_asyncio.fixture
async def model_type_repository(
    sql_connector: AsyncSqlConnector,
) -> ModelTypeRepository:
    """
    Create a ProviderTemplateRepository using the test database.
    """
    return ModelTypeRepository(sql_connector)


# Fixture for ProviderTemplateRepository based on test_db
@pytest_asyncio.fixture
async def setup_mappers():
    mapper_manager.add_mapper(mapping_pair=(ModelInstanceDto, ModelInstance), mapper=ModelInstanceDTOEntityMapper)


# Fixture for creating a test provider template
@pytest_asyncio.fixture
async def provider_template(
    db_session: AsyncSession,
) -> ProviderTemplate:
    """
    Create and persist a test provider template.
    """
    provider_template = ProviderTemplate(
        id=uuid.uuid4(),
        name="Test Provider Template",
        description="Test provider template for testing",
        overridable=True,
    )

    db_session.add(provider_template)
    await db_session.commit()
    await db_session.refresh(provider_template)

    return provider_template


# Fixture for creating a test property type
@pytest_asyncio.fixture
async def property_type(db_session: AsyncSession) -> ProviderPropertyType:
    """
    Create and persist a test property type.
    """
    property_type = ProviderPropertyType(id=uuid.uuid4(), description="Test Property Type", type="text")

    db_session.add(property_type)
    await db_session.commit()
    await db_session.refresh(property_type)

    return property_type


# Fixture for creating a test property template
@pytest_asyncio.fixture
async def property_template(
    db_session: AsyncSession,
    provider_template: ProviderTemplate,
    property_type: ProviderPropertyType,
) -> ProviderPropertyTemplate:
    """
    Create and persist a test property template associated with the provider template.
    """
    property_template = ProviderPropertyTemplate(
        id=uuid.uuid4(),
        label="Test Property",
        key="test_property",
        provider_template_id=provider_template.id,
        property_type_ref=property_type,
        required=True,
        default_value=None,
    )

    db_session.add(property_template)
    await db_session.commit()
    await db_session.refresh(property_template)

    return property_template


# Fixture for ProviderInstanceRepository based on test_db
@pytest_asyncio.fixture
async def provider_instance_repository(
    sql_connector: AsyncSqlConnector,
) -> ProviderInstanceRepository:
    """
    Create a ProviderInstanceRepository using the test database.
    """
    return ProviderInstanceRepository(sql_connector)


# Fixture for creating a test provider instance
@pytest_asyncio.fixture
async def provider_instance(
    db_session: AsyncSession,
    provider_template: ProviderTemplate,
) -> ProviderInstance:
    """
    Create and persist a test provider instance.
    """
    provider_instance = ProviderInstance(
        id=uuid.uuid4(),
        provider_template_id=provider_template.id,
        name="Test Provider Instance",
    )

    db_session.add(provider_instance)
    await db_session.commit()
    await db_session.refresh(provider_instance)

    return provider_instance


# Fixture for creating a test property instance
@pytest_asyncio.fixture
async def property_instance(
    db_session: AsyncSession,
    provider_instance: ProviderInstance,
    property_template: ProviderPropertyTemplate,
) -> ProviderPropertyInstance:
    """
    Create and persist a test property instance.
    """
    property_instance = ProviderPropertyInstance(
        id=uuid.uuid4(),
        value="test_value",
        provider_instance_id=provider_instance.id,
        property_template_id=property_template.id,
    )

    db_session.add(property_instance)
    await db_session.commit()
    await db_session.refresh(property_instance)

    return property_instance


# Model-related fixtures


# Fixture for ModelTemplateRepository based on test_db
@pytest_asyncio.fixture
async def model_template_repository(
    sql_connector: AsyncSqlConnector,
) -> ModelTemplateRepository:
    """
    Create a ModelTemplateRepository using the test database.
    """
    return ModelTemplateRepository(sql_connector)


# Fixture for creating a test model type
@pytest_asyncio.fixture
async def model_type(db_session: AsyncSession) -> ModelType:
    """
    Create and persist a test model type.
    """
    # Generate a unique name for each test to avoid unique constraint violations
    unique_name = f"chat_{uuid.uuid4().hex[:8]}"

    model_type = ModelType(id=uuid.uuid4(), name=unique_name)

    db_session.add(model_type)
    await db_session.commit()
    await db_session.refresh(model_type)

    return model_type


# Fixture for creating a test model capability
@pytest_asyncio.fixture
async def model_capability(db_session: AsyncSession) -> Capability:
    """
    Create and persist a test model capability.
    """
    model_capability = Capability(
        id=uuid.uuid4(),
        name="function_calling",
        description="The model supports function calling",
        value="true",
    )

    db_session.add(model_capability)
    await db_session.commit()
    await db_session.refresh(model_capability)

    return model_capability


# Fixture for creating a test model template
@pytest_asyncio.fixture
async def model_template(
    db_session: AsyncSession,
    model_type: ModelType,
    provider_template: ProviderTemplate,
) -> ModelTemplate:
    """
    Create and persist a test model template.
    """
    model_template = ModelTemplate(
        id=uuid.uuid4(),
        name="Test Model Template",
        description="Test model template for testing",
        type_id=model_type.id,
        provider_template_id=provider_template.id,
    )

    db_session.add(model_template)
    await db_session.commit()
    await db_session.refresh(model_template)

    return model_template


# Fixture for associating a capability with a model template
@pytest_asyncio.fixture
async def model_capabilities(
    db_session: AsyncSession,
    model_template: ModelTemplate,
    model_capability: Capability,
) -> ModelTemplateCapability:
    """
    Create and persist a capability association for a model template.
    """
    model_capabilities = ModelTemplateCapability(
        id=uuid.uuid4(),
        model_template_id=model_template.id,
        model_capability_id=model_capability.id,
    )

    db_session.add(model_capabilities)
    await db_session.commit()
    await db_session.refresh(model_capabilities)

    return model_capabilities


# Fixture for creating a test model property type
@pytest_asyncio.fixture
async def model_property_type(db_session: AsyncSession) -> ModelPropertyType:
    """
    Create and persist a test model property type.
    """
    model_property_type = ModelPropertyType(
        id=uuid.uuid4(),
        name="Max Tokens",
        description="Maximum number of tokens",
        type="number",
    )

    db_session.add(model_property_type)
    await db_session.commit()
    await db_session.refresh(model_property_type)

    return model_property_type


# Fixture for creating a test model property template
@pytest_asyncio.fixture
async def model_property_template(
    db_session: AsyncSession,
    model_template: ModelTemplate,
    model_property_type: ModelPropertyType,
) -> ModelPropertyTemplate:
    """
    Create and persist a test model property template.
    """
    model_property_template = ModelPropertyTemplate(
        id=uuid.uuid4(),
        label="Test Model Property",
        key="test_model_property",
        model_template_id=model_template.id,
        model_property_type_id=model_property_type.id,
        required=True,
        default_value=None,
    )

    db_session.add(model_property_template)
    await db_session.commit()
    await db_session.refresh(model_property_template)

    return model_property_template


# Fixture for ModelInstanceRepository based on test_db
@pytest_asyncio.fixture
async def model_instance_repository(
    sql_connector: AsyncSqlConnector,
) -> ModelInstanceRepository:
    """
    Create a ModelInstanceRepository using the test database.
    """
    repository = ModelInstanceRepository(sql_connector)
    di[ModelInstanceRepository] = repository
    return repository


# Fixture for creating a test model instance
@pytest_asyncio.fixture
async def model_instance(
    db_session: AsyncSession,
    model_template: ModelTemplate,
) -> ModelInstance:
    """
    Create and persist a test model instance.
    """
    model_instance = ModelInstance(id=uuid.uuid4(), model_template_id=model_template.id, name="Test Model Instance")

    db_session.add(model_instance)
    await db_session.commit()
    await db_session.refresh(model_instance)

    return model_instance


# Fixture for creating a test model property instance
@pytest_asyncio.fixture
async def model_property_instance(
    db_session: AsyncSession,
    model_instance: ModelInstance,
    model_property_template: ModelPropertyTemplate,
) -> ModelPropertyInstance:
    """
    Create and persist a test model property instance.
    """
    model_property_instance = ModelPropertyInstance(
        id=uuid.uuid4(),
        value="1024",
        model_instance_id=model_instance.id,
        model_property_template_id=model_property_template.id,
    )

    db_session.add(model_property_instance)
    await db_session.commit()
    await db_session.refresh(model_property_instance)

    return model_property_instance


# Fixture for creating a test owner enum
@pytest_asyncio.fixture
async def owner_enum(db_session: AsyncSession) -> OwnerType:
    """
    Create and persist a test owner enum.
    """
    # Generate a unique name for each test to avoid unique constraint violations
    unique_name = f"user_{uuid.uuid4().hex[:8]}"
    owner_enum = OwnerType(
        id=uuid.uuid4(),
        name=unique_name,
    )

    db_session.add(owner_enum)
    await db_session.commit()
    await db_session.refresh(owner_enum)

    return owner_enum


# Fixture for ProviderModelRepository based on test_db
@pytest_asyncio.fixture
async def provider_model_repository(
    sql_connector: AsyncSqlConnector,
) -> ProviderModelRepository:
    """
    Create a ProviderModelRepository using the test database.
    """
    repository = ProviderModelRepository(sql_connector)
    di[ProviderModelRepository] = repository
    return repository


# Fixture for creating a test provider model
@pytest_asyncio.fixture
async def provider_model(
    db_session: AsyncSession,
    model_instance: ModelInstance,
    provider_instance: ProviderInstance,
    owner_enum: OwnerType,
) -> ProviderModel:
    """
    Create and persist a test provider model.
    """
    provider_model = ProviderModel(
        id=uuid.uuid4(),
        model_instance_id=model_instance.id,
        provider_instance_id=provider_instance.id,
        owner_id=uuid.uuid4(),  # Random owner ID
        owner_type_id=owner_enum.id,
    )

    db_session.add(provider_model)
    await db_session.commit()
    await db_session.refresh(provider_model)

    return provider_model


# Fixture for creating multiple provider models for pagination tests
@pytest_asyncio.fixture
async def multiple_provider_models(
    db_session: AsyncSession,
    model_instance: ModelInstance,
    provider_instance: ProviderInstance,
    owner_enum: OwnerType,
) -> list[ProviderModel]:
    """
    Create and persist multiple provider models for pagination testing.
    """
    provider_models = []

    # Create 15 provider models for pagination testing
    for _i in range(15):
        provider_model = ProviderModel(
            id=uuid.uuid4(),
            model_instance_id=model_instance.id,
            provider_instance_id=provider_instance.id,
            owner_id=uuid.uuid4(),  # Random owner ID
            owner_type_id=owner_enum.id,
        )

        db_session.add(provider_model)
        provider_models.append(provider_model)

    await db_session.commit()

    # Refresh all models
    for model in provider_models:
        await db_session.refresh(model)

    return provider_models


@pytest.fixture
def postgres_dsn(test_db: AsyncPostgresConf) -> str:
    """
    Return the PostgreSQL DSN string for the test database.
    This is needed for tests that need direct access to the DSN.
    """
    return test_db.url.render_as_string(hide_password=False)
