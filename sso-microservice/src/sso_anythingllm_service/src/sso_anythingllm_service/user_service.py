from kink import inject

from sso_anythingllm_dto.config.anything_llm import AnythingLLMConfig
from sso_anythingllm_dto.user import AnythingLLMUserDto
from sso_anythingllm_dto_entity_mapper.user import AnythingLLMUserDTOEntityMapper
from sso_anythingllm_repository import AnythingLLMRepository
from sso_anythingllm_repository.config import AnythingLLMConfig as RepoConfig
from sso_anythingllm_repository.interfaces.anything_llm_repository_interface import AnythingLLMRepositoryInterface
from sso_anythingllm_repository.interfaces.user_repository_interface import UserRepositoryInterface
from sso_anythingllm_service.interfaces.user_service_interface import UserServiceInterface


@inject(alias=UserServiceInterface)
class UserService(UserServiceInterface):
    def __init__(self, user_repository: UserRepositoryInterface, anything_llm_config: AnythingLLMConfig):
        self.user_repository = user_repository
        self.mapper = AnythingLLMUserDTOEntityMapper()
        self.anything_llm_config = anything_llm_config

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

    async def create_user_in_anything_llm(self, user: AnythingLLMUserDto, api_key: str) -> int:
        """Creates the user in AnythingLLM and returns the user ID."""
        config: RepoConfig = RepoConfig(
            base_url=self.anything_llm_config.url, verify_ssl=self.anything_llm_config.verify_ssl, api_key=api_key
        )
        repo: AnythingLLMRepositoryInterface = AnythingLLMRepository(config=config)
        result = await repo.create_user(
            user_data={"username": user.keycloak_id, "role": user.role, "password": "default-user-password"}
        )
        return int(result["user"]["id"])

    # ──────────────────────────── UPDATE ────────────────────────────
    async def update(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
        entity = await self.user_repository.update(self.mapper.to_target(user))
        return self.mapper.from_target(entity)

    async def update_user_in_anything_llm(self, user: AnythingLLMUserDto, api_key: str) -> int:
        """Creates the user in AnythingLLM and returns the user ID."""
        config: RepoConfig = RepoConfig(
            base_url=self.anything_llm_config.url, verify_ssl=self.anything_llm_config.verify_ssl, api_key=api_key
        )
        repo: AnythingLLMRepositoryInterface = AnythingLLMRepository(config=config)
        if user.internal_id is None:
            raise ValueError("User needs to have an internal AnythingLLM id to be updatable.")
        else:
            result = await repo.update_user(
                user_id=user.internal_id,
                user_data={
                    "username": user.keycloak_id,
                    "role": user.role,
                    "password": "default-user-password",
                    "suspended": 0,
                },
            )
        return int(result["user"]["id"])

    # ──────────────────────────── DELETE ────────────────────────────
    async def delete(self, user: AnythingLLMUserDto):
        await self.user_repository.delete_by_keycloak_id(keycloak_id=user.keycloak_id)
