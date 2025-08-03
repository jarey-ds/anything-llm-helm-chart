import logging
from typing import List

from kink import inject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing_extensions import override

from sso_anythingllm_entity.api_key import ApiKey
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError
from sso_anythingllm_repository.interfaces.api_key_repository_interface import ApiKeyRepositoryInterface


@inject(alias=ApiKeyRepositoryInterface)
class ApiKeyRepository(ApiKeyRepositoryInterface):
    """Repository in charge of the ApiKey entity."""

    def __init__(self, db_config: AsyncPostgresConf):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def _get_session(self) -> AsyncSession:
        """Get an async database session."""
        return AsyncSession(self.db_config.engine)

    @override
    async def get_by_value(self, value: str) -> ApiKey:
        """Get an API key by its value."""
        async with self._get_session() as session:
            try:
                statement = select(ApiKey).where(ApiKey.value == value)
                result = await session.execute(statement)
                api_key = result.scalar_one_or_none()

                if not api_key:
                    raise ValidationError(f"API key with value '{value}' not found")

                return api_key
            except Exception as e:
                self.logger.error(f"Error retrieving API key by value '{value}': {e}")
                raise ValidationError(f"Failed to retrieve API key: {str(e)}")

    # ──────────────────────────── CREATE ────────────────────────────
    @override
    async def save(self, api_key: ApiKey) -> ApiKey:
        """Save a new API key to the database."""
        async with self._get_session() as session:
            try:
                # Check if API key already exists
                if api_key.value:
                    statement = select(ApiKey).where(ApiKey.value == api_key.value)
                    result = await session.execute(statement)
                    existing_api_key = result.scalar_one_or_none()
                    if existing_api_key:
                        raise ValidationError(f"API key with value '{api_key.value}' already exists")

                session.add(api_key)
                await session.commit()
                await session.refresh(api_key)

                self.logger.info(f"Successfully created API key with value '{api_key.value}'")
                return api_key
            except ValidationError:
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error creating API key: {e}")
                raise ValidationError(f"Failed to create API key: {str(e)}")

    # ──────────────────────────── UPDATE ────────────────────────────
    @override
    async def update(self, api_key: ApiKey) -> ApiKey:
        """Update an existing API key in the database."""
        async with self._get_session() as session:
            try:
                # Check if API key exists and get the existing API key
                statement = select(ApiKey).where(ApiKey.value == api_key.value)
                result = await session.execute(statement)
                db_api_key = result.scalar_one_or_none()

                if not db_api_key:
                    raise ValidationError(f"API key with value '{api_key.value}' not found")

                # Update fields (in this case, ApiKey only has one field, so we'll just return the existing one)
                # If ApiKey had more fields, we would update them here
                await session.commit()
                await session.refresh(db_api_key)

                self.logger.info(f"Successfully updated API key with value '{api_key.value}'")
                return db_api_key
            except ValidationError:
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error updating API key: {e}")
                raise ValidationError(f"Failed to update API key: {str(e)}")

    # ──────────────────────────── DELETE ────────────────────────────
    @override
    async def delete_by_value(self, value: str) -> None:
        """Delete an API key by its value."""
        async with self._get_session() as session:
            try:
                # Check if API key exists and get the API key to delete
                statement = select(ApiKey).where(ApiKey.value == value)
                result = await session.execute(statement)
                api_key = result.scalar_one_or_none()

                if not api_key:
                    raise ValidationError(f"API key with value '{value}' not found")

                await session.delete(api_key)
                await session.commit()

                self.logger.info(f"Successfully deleted API key with value '{value}'")
            except ValidationError:
                raise
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error deleting API key: {e}")
                raise ValidationError(f"Failed to delete API key: {str(e)}")

    # ──────────────────────────── ADDITIONAL CRUD OPERATIONS ────────────────────────────
    @override
    async def get_all_api_keys(self) -> list[ApiKey]:
        """Get all API keys from the database."""
        async with self._get_session() as session:
            try:
                statement = select(ApiKey)
                result = await session.execute(statement)
                return list(result.scalars().all())
            except Exception as e:
                self.logger.error(f"Error retrieving all API keys: {e}")
                raise ValidationError(f"Failed to retrieve API keys: {str(e)}")

    @override
    async def api_key_exists(self, value: str) -> bool:
        """Check if an API key exists by its value."""
        try:
            await self.get_by_value(value)
            return True
        except ValidationError:
            return False

    @override
    async def count_api_keys(self) -> int:
        """Get the total number of API keys in the database."""
        async with self._get_session() as session:
            try:
                statement = select(ApiKey)
                result = await session.execute(statement)
                return len(result.scalars().all())
            except Exception as e:
                self.logger.error(f"Error counting API keys: {e}")
                raise ValidationError(f"Failed to count API keys: {str(e)}")

    # ──────────────────────────── LEGACY METHODS ────────────────────────────
    @override
    async def create(self, api_key: ApiKey) -> ApiKey:
        """Legacy method - creates a new API key entry in the database."""
        return await self.save(api_key)

    @override
    async def delete(self, api_key: ApiKey) -> None:
        """Legacy method - deletes an API key entry in the database."""
        await self.delete_by_value(api_key.value)

    @override
    async def get_api_keys(self) -> List[ApiKey]:
        """Legacy method - gets the set of API keys that exist in the database."""
        return await self.get_all_api_keys()
