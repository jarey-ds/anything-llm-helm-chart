from kink import inject
from typing_extensions import override

from sso_anythingllm_entity.user import User
from sso_anythingllm_repository.interfaces.user_repository_interface import UserRepositoryInterface


@inject(alias=UserRepositoryInterface)
class UserRepository(UserRepositoryInterface):
    """Repository in charge of the ModelInstance entity."""

    @override
    async def get_by_keycloak_id(self, keycloak_id: str) -> User: ...

    @override
    async def get_by_anythingllm_id(self, anythingllm_id: int) -> User: ...

    # ──────────────────────────── CREATE ────────────────────────────
    @override
    async def save(self, user: User) -> User: ...

    # ──────────────────────────── UPDATE ────────────────────────────
    @override
    async def update(self, user: User) -> User: ...

    # ──────────────────────────── DELETE ────────────────────────────
    @override
    async def delete_by_keycloak_id(self, id: str): ...
