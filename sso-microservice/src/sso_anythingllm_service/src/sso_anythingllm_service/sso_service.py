from kink import inject

from sso_anythingllm_dto.config.anything_llm import AnythingLLMConfig
from sso_anythingllm_repository import AnythingLLMConfig as RepoConfig
from sso_anythingllm_repository import AnythingLLMRepository
from sso_anythingllm_repository.interfaces.anything_llm_repository_interface import AnythingLLMRepositoryInterface
from sso_anythingllm_service.interfaces.sso_service_interface import SSOServiceInterface


@inject(alias=SSOServiceInterface)
class SSOService(SSOServiceInterface):
    def __init__(self, anything_llm_config: AnythingLLMConfig):
        self.anything_llm_config = anything_llm_config

    # ──────────────────────────── GET ────────────────────────────
    async def get_sso_url_for_user(self, anything_llm_user_id: int, api_key: str) -> str:
        """Obtain the SSO single use URL for the user, via AnythingLLM's Rest API"""
        config: RepoConfig = RepoConfig(
            base_url=self.anything_llm_config.url, verify_ssl=self.anything_llm_config.verify_ssl, api_key=api_key
        )
        repo: AnythingLLMRepositoryInterface = AnythingLLMRepository(config=config)
        result = repo.issue_auth_token(user_id=anything_llm_user_id)
        return str(result)
