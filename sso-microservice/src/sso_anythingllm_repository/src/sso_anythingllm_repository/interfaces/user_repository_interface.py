from typing import Protocol

from sso_anythingllm_entity.user import User


class UserRepositoryInterface(Protocol):
    """Interface for Capability repository operations."""

    # ──────────────────────────── GET ────────────────────────────
    async def get_by_keycloak_id(self, keycloak_id: str) -> User: ...

    async def get_by_anythingllm_id(self, anythingllm_id: int) -> User: ...

    # ──────────────────────────── CREATE ────────────────────────────
    async def save(self, user: User) -> User: ...

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, user: User) -> User: ...

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete_by_keycloak_id(self, id: str): ...
