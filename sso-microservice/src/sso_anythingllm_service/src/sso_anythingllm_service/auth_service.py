from kink import inject

from sso_anythingllm_dto.config.anything_llm import AnythingLLMConfig
from sso_anythingllm_repository import AnythingLLMRepository
from sso_anythingllm_repository.config import AnythingLLMConfig as RepoConfig
from sso_anythingllm_repository.interfaces.anything_llm_repository_interface import AnythingLLMRepositoryInterface
from sso_anythingllm_service.interfaces.auth_service_interface import AuthServiceInterface


@inject(alias=AuthServiceInterface)
class AuthService(AuthServiceInterface):
    def __init__(self, anything_llm_config: AnythingLLMConfig):
        self.anything_llm_config = anything_llm_config

    async def obtain_auth_token_for_admin(self) -> str:
        """Obtain the SSO single use URL for the user, via AnythingLLM's Rest API"""
        config: RepoConfig = RepoConfig(
            base_url=self.anything_llm_config.url,
            verify_ssl=self.anything_llm_config.verify_ssl,
        )
        repo: AnythingLLMRepositoryInterface = AnythingLLMRepository(config=config)
        result = await repo.obtain_auth_token(
            credentials_data={
                "username": self.anything_llm_config.admin_user,
                "password": self.anything_llm_config.admin_password,
            }
        )
        return result["token"]
