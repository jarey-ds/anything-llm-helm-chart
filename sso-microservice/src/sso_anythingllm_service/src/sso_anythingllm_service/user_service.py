from kink import inject

from sso_anythingllm_dto.user import AnythingLLMUserDto
from sso_anythingllm_dto_entity_mapper.user import AnythingLLMUserDTOEntityMapper
from sso_anythingllm_repository.interfaces.user_repository_interface import UserRepositoryInterface
from sso_anythingllm_service.interfaces.user_service_interface import UserServiceInterface


@inject(alias=UserServiceInterface)
class UserService(UserServiceInterface):
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
    ):
        self.user_repository = user_repository
        self.mapper = AnythingLLMUserDTOEntityMapper()

    # ──────────────────────────── GET ────────────────────────────
    async def get_user_by_keycloak_id(self, keycloak_id: str) -> AnythingLLMUserDto:
        """Get a provider property type by ID"""
        entity = await self.user_repository.get_by_keycloak_id(keycloak_id)
        return self.mapper.from_target(entity)

    async def get_user_by_anythingllm_id(self, anythingllm_id: int) -> AnythingLLMUserDto:
        """Get a provider property type by ID"""
        entity = await self.user_repository.get_by_anythingllm_id(anythingllm_id)
        return self.mapper.from_target(entity)

    # ──────────────────────────── CREATE ────────────────────────────
    async def save(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
        entity = await self.user_repository.save(self.mapper.to_target(user))
        return self.mapper.from_target(entity)

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
        entity = await self.user_repository.update(self.mapper.to_target(user))
        return self.mapper.from_target(entity)

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete(self, user: AnythingLLMUserDto):
        await self.user_repository.delete_by_keycloak_id(keycloak_id=user.keycloak_id)
