"""Model instance service interface using Protocol."""

from typing import Protocol

from sso_anythingllm_dto.user import AnythingLLMUserDto


class UserServiceInterface(Protocol):
    """Interface for model instance service operations."""

    # ──────────────────────────── GET ────────────────────────────
    async def get_user_by_keycloak_id(self, keycloak_id: str) -> AnythingLLMUserDto:
        """Get a provider property type by ID"""
        ...

    async def get_user_by_anythingllm_id(self, anythingllm_id: int) -> AnythingLLMUserDto:
        """Get a provider property type by ID"""
        ...

    # ──────────────────────────── CREATE ────────────────────────────
    async def save(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto: ...

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto: ...

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete(self, user: AnythingLLMUserDto): ...

    async def create_user_in_anything_llm(self, user: AnythingLLMUserDto, api_key: str) -> int:
        """Creates the user in AnythingLLM and returns the user ID."""
        ...

    async def update_user_in_anything_llm(self, user: AnythingLLMUserDto, api_key: str) -> int:
        """Updates the user in AnythingLLM and returns the user ID."""
        ...
