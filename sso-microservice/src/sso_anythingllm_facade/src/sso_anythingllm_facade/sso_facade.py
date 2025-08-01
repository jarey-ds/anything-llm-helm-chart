"""Model instance facade module for orchestrating model instance operations."""

from kink import inject

from sso_anythingllm_dto.user import KeycloakUserDto
from sso_anythingllm_facade.interfaces import SSOFacadeInterface
from sso_anythingllm_service.interfaces.sso_service_interface import SSOServiceInterface
from sso_anythingllm_service.interfaces.user_service_interface import UserServiceInterface


@inject(alias=SSOFacadeInterface)
class SSOFacade(SSOFacadeInterface):
    """Facade for orchestrating SSO use-case operations."""

    def __init__(
        self,
        sso_service: SSOServiceInterface,
        user_service: UserServiceInterface,
    ):
        """Initialize the ModelInstanceFacade with required service.

        Args:
            model_instance_service: Service for model instance operations
        """
        self.sso_service = sso_service
        self.user_service = user_service

    async def get_anything_llm_sso_url(self, user: KeycloakUserDto) -> str:
        """
        Get user's SSO temporal URL by User information on Keycloak.

        Args:
            user (UserDTO): The data parsed from the keycloak token that represents an user.

        Returns:
            str: AnythingLLM's temporarily access URL by its simple SSO integration.
        """
        return ""
