"""Model instance facade module for orchestrating model instance operations."""

from typing import Dict

from kink import di, inject

from sso_anythingllm_dto.config.keycloak import KeycloakTokenConfig
from sso_anythingllm_dto.user import AnythingLLMUserDto
from sso_anythingllm_dto_to_mapper.user_mapper import AnythingLLMUserDtoToMapper
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
            sso_service: Service for sso related operations
            user_service: Service for user-related operations
        """
        self.sso_service = sso_service
        self.user_service = user_service

    async def get_anything_llm_sso_url(self, user: Dict) -> str:
        """
        Get user's SSO temporal URL by User information on Keycloak.

        Args:
            user (Dict): The data parsed from the keycloak token that represents an user, in key-value format.

        Returns:
            str: AnythingLLM's temporarily access URL by its simple SSO integration.
        """
        # Map user dict to AnythingLLMUserDto

        incoming_user: AnythingLLMUserDto = AnythingLLMUserDtoToMapper(
            keycloak_config=di[KeycloakTokenConfig]
        ).from_target(target=user)
        # Check if user exist on local database
        db_user: AnythingLLMUserDto = await self.user_service.get_user_by_keycloak_id(
            keycloak_id=incoming_user.keycloak_id
        )
        if db_user is None:
            # If user doesn't exist, create the user at database level.
            user = await self.user_service.save_user_in_anythingllm_and_db(user=incoming_user)
        else:
            # If user does exist, check that the groups coming from keycloak
            # and the groups at database level are consistent.
            # we assume there is no local modification made manually at AnythingLLM's side, performed by admin users
            # if this assumption changes, this business logic needs to be aligned.
            if db_user.role != incoming_user.role:
                # Update at API level.
                await self.user_service.update(user=db_user)

        self.sso_service.get_sso_url_for_user()

        return ""

    async def save_user_in_anythingllm_and_db(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
        """Stores the user first in the AnythingLLM Rest API. and then on local database"""
        user: AnythingLLMUserDto = self.user_service.save_in_anything_llm(user=user)
        # Save user in DB with the internal_id from AnythingLLM populated as a result of the Rest API call.
        user = await self.user_service.save(user=user)
        return user

    async def check_user_in_anythingllm_and_update_on_db(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
        # We update the user no matter what, to avoid getting the user,
        # inspecting if roles are the same and if they missmatch
        # performing another call to update the user on AnythingLLM; since no matter what the use-case is, we would need
        # to perform at least 1 API call in this use-case, we minimise the number of calls
        # to be only 1 instead of 2 in the worst case scenario.
        if user.internal_id is None:
            raise ValueError("If the user exists in the database it should have an AnythingLLM internal ID.")

        user = await self.user_service.update(user=user)
        user = await self.user_service.update_user_in_anything_llm(user=user)
        return user
