"""ApiKey service interface using Protocol."""

from typing import Protocol

from sso_anythingllm_dto.api_key import ApiKeyDto


class ApiKeyServiceInterface(Protocol):
    """Interface for ApiKey service operations."""

    # ──────────────────────────── GET ────────────────────────────
    async def get_api_key_by_value(self, value: str) -> ApiKeyDto:
        """Get an API key by its value"""
        ...

    async def get_all_api_keys(self) -> list[ApiKeyDto]:
        """Get all API keys"""
        ...

    async def api_key_exists(self, value: str) -> bool:
        """Check if an API key exists by its value"""
        ...

    async def count_api_keys(self) -> int:
        """Get the total number of API keys"""
        ...

    # ──────────────────────────── CREATE ────────────────────────────
    async def save(self, api_key: ApiKeyDto) -> ApiKeyDto:
        """Save a new API key"""
        ...

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, api_key: ApiKeyDto) -> ApiKeyDto:
        """Update an existing API key"""
        ...

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete_by_value(self, value: str) -> None:
        """Delete an API key by its value"""
        ...

    # ──────────────────────────── LEGACY METHODS ────────────────────────────
    async def create(self, api_key: ApiKeyDto) -> ApiKeyDto:
        """Legacy method: Create a new API key (alias for save)"""
        ...

    async def delete(self, api_key: ApiKeyDto) -> None:
        """Legacy method: Delete an API key (alias for delete_by_value)"""
        ...

    async def get_api_keys(self) -> list[ApiKeyDto]:
        """Legacy method: Get all API keys (alias for get_all_api_keys)"""
        ...
