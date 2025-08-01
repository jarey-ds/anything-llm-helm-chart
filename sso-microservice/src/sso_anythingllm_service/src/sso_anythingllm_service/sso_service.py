from kink import inject

from sso_anythingllm_service.interfaces.sso_service_interface import SSOServiceInterface


@inject(alias=SSOServiceInterface)
class SSOService(SSOServiceInterface):
    # ──────────────────────────── GET ────────────────────────────
    async def get_sso_url_for_user(self, anything_llm_user_id: int) -> str:
        """Obtain the SSO single use URL for the user, via AnythingLLM's Rest API"""
        return ""
