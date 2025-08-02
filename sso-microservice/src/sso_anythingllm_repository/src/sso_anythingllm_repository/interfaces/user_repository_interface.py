from typing import Protocol

from sso_anythingllm_entity.user import User


class UserRepositoryInterface(Protocol):
    """Interface for User repository operations."""

    # ──────────────────────────── GET ────────────────────────────
    async def get_by_keycloak_id(self, keycloak_id: str) -> User: ...

    async def get_by_anythingllm_id(self, anythingllm_id: int) -> User: ...

    # ──────────────────────────── CREATE ────────────────────────────
    async def save(self, user: User) -> User: ...

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, user: User) -> User: ...

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete_by_keycloak_id(self, keycloak_id: str) -> None: ...

    # ──────────────────────────── ADDITIONAL CRUD OPERATIONS ────────────────────────────
    async def get_all_users(self) -> list[User]: ...

    async def get_users_by_role(self, role: str) -> list[User]: ...

    async def user_exists(self, keycloak_id: str) -> bool: ...

    async def count_users(self) -> int: ...
