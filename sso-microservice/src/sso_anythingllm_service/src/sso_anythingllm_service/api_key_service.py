from kink import inject

from sso_anythingllm_dto.api_key import ApiKeyDto
from sso_anythingllm_dto_entity_mapper.api_key import ApiKeyDTOEntityMapper
from sso_anythingllm_repository.interfaces.api_key_repository_interface import ApiKeyRepositoryInterface
from sso_anythingllm_service.interfaces.api_key_service_interface import ApiKeyServiceInterface


@inject(alias=ApiKeyServiceInterface)
class ApiKeyService(ApiKeyServiceInterface):
    """Service for managing API keys with full CRUD operations."""

    def __init__(self, api_key_repository: ApiKeyRepositoryInterface):
        self.api_key_repository = api_key_repository
        self.mapper = ApiKeyDTOEntityMapper()

    # ──────────────────────────── GET ────────────────────────────
    async def get_api_key_by_value(self, value: str) -> ApiKeyDto:
        """Get an API key by its value."""
        entity = await self.api_key_repository.get_by_value(value)
        return self.mapper.from_target(entity)

    async def get_all_api_keys(self) -> list[ApiKeyDto]:
        """Get all API keys."""
        entities = await self.api_key_repository.get_all_api_keys()
        return [self.mapper.from_target(entity) for entity in entities]

    async def api_key_exists(self, value: str) -> bool:
        """Check if an API key exists by its value."""
        return await self.api_key_repository.api_key_exists(value)

    async def count_api_keys(self) -> int:
        """Get the total number of API keys."""
        return await self.api_key_repository.count_api_keys()

    # ──────────────────────────── CREATE ────────────────────────────
    async def save(self, api_key: ApiKeyDto) -> ApiKeyDto:
        """Save a new API key."""
        entity = await self.api_key_repository.save(self.mapper.to_target(api_key))
        return self.mapper.from_target(entity)

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, api_key: ApiKeyDto) -> ApiKeyDto:
        """Update an existing API key."""
        entity = await self.api_key_repository.update(self.mapper.to_target(api_key))
        return self.mapper.from_target(entity)

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete_by_value(self, value: str) -> None:
        """Delete an API key by its value."""
        await self.api_key_repository.delete_by_value(value)

    # ──────────────────────────── LEGACY METHODS ────────────────────────────
    async def create(self, api_key: ApiKeyDto) -> ApiKeyDto:
        """Legacy method: Create a new API key (alias for save)."""
        return await self.save(api_key)

    async def delete(self, api_key: ApiKeyDto) -> None:
        """Legacy method: Delete an API key (alias for delete_by_value)."""
        await self.delete_by_value(api_key.value)

    async def get_api_keys(self) -> list[ApiKeyDto]:
        """Legacy method: Get all API keys (alias for get_all_api_keys)."""
        return await self.get_all_api_keys()
