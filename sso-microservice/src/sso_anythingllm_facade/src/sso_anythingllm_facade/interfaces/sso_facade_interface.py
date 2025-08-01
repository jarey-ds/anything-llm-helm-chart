"""Capability facade interface using Protocol."""

from typing import Dict, Protocol


class SSOFacadeInterface(Protocol):
    """Facade for managing all SSO use-case operations."""

    async def get_anything_llm_sso_url(self, user: Dict) -> str:
        """
        Get user's SSO temporal URL by User information on Keycloak.

        Args:
            user (UserDTO): The data parsed from the keycloak token that represents an user.

        Returns:
            str: AnythingLLM's temporarily access URL by its simple SSO integration.
        """
        ...
