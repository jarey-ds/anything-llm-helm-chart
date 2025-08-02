"""Model instance facade module for orchestrating model instance operations."""

from typing import Dict, List

from kink import di, inject

from sso_anythingllm_dto import ApiKeyDto
from sso_anythingllm_dto.config.keycloak import KeycloakTokenConfig
from sso_anythingllm_dto.user import AnythingLLMUserDto
from sso_anythingllm_dto_to_mapper.user_mapper import AnythingLLMUserDtoToMapper
from sso_anythingllm_facade.interfaces import SSOFacadeInterface
from sso_anythingllm_service.interfaces.api_key_service_interface import ApiKeyServiceInterface
from sso_anythingllm_service.interfaces.auth_service_interface import AuthServiceInterface
from sso_anythingllm_service.interfaces.sso_service_interface import SSOServiceInterface
from sso_anythingllm_service.interfaces.user_service_interface import UserServiceInterface


@inject(alias=SSOFacadeInterface)
class SSOFacade(SSOFacadeInterface):
    """Facade for orchestrating SSO use-case operations."""

    def __init__(
        self,
        sso_service: SSOServiceInterface,
        user_service: UserServiceInterface,
        api_key_service: ApiKeyServiceInterface,
        auth_service: AuthServiceInterface,
    ):
        """Initialize the ModelInstanceFacade with required service.

        Args:
            sso_service: Service for sso related operations
            user_service: Service for user-related operations
        """
        self.sso_service = sso_service
        self.user_service = user_service
        self.api_key_service = api_key_service
        self.auth_service = auth_service

    async def get_anything_llm_sso_url(self, user: Dict) -> str:
        """
        Get user's SSO temporal URL by User information on Keycloak.

        Args:
            user (Dict): The data parsed from the keycloak token that represents an user, in key-value format.

        Returns:
            str: AnythingLLM's temporarily access URL by its simple SSO integration.
        """
        # Get or generate AnythingLLM's API KEY
        keys: List[ApiKeyDto] = await self.api_key_service.get_all_api_keys()
        if keys and len(keys) > 0:
            api_key: ApiKeyDto = keys[0]
        else:
            # Get auth token for the user.
            auth_token: str = await self.auth_service.obtain_auth_token_for_admin()
            api_key: ApiKeyDto = await self.api_key_service.generate_new_api_key(auth_token=auth_token)
            await self.api_key_service.create(api_key=api_key)

        # Map user dict to AnythingLLMUserDto
        incoming_user: AnythingLLMUserDto = AnythingLLMUserDtoToMapper(
            keycloak_config=di[KeycloakTokenConfig]
        ).from_target(target=user)
        # Check if user exist on local database
        db_user: AnythingLLMUserDto = await self.user_service.get_user_by_keycloak_id(
            keycloak_id=incoming_user.keycloak_id
        )
        if db_user is None:
            # Create the user in AnythingLLM's side, using the API Rest
            anything_llm_user_id: int = await self.user_service.create_user_in_anything_llm(
                user=incoming_user, api_key=api_key.value
            )
            incoming_user.internal_id = anything_llm_user_id
            # If user doesn't exist, create the user at database level.
            processed_user: AnythingLLMUserDto = await self.user_service.save(user=incoming_user)
        else:
            # If user does exist, check that the groups coming from keycloak
            # and the groups at database level are consistent.
            # we assume there is no local modification made manually at AnythingLLM's side, performed by admin users
            # if this assumption changes, this business logic needs to be aligned.
            if db_user.role != incoming_user.role:
                # Update at API level.
                db_user.role = incoming_user.role
                processed_user: AnythingLLMUserDto = await self.user_service.update(user=db_user)
                await self.user_service.update_user_in_anything_llm(user=db_user, api_key=api_key.value)
            else:
                processed_user: AnythingLLMUserDto = db_user

        if processed_user.internal_id is None:
            raise ValueError(
                "Business logic error, the user should always have an internal AnythingLLM identifier here."
            )
        await self.sso_service.get_sso_url_for_user(
            anything_llm_user_id=int(processed_user.internal_id), api_key=api_key.value
        )

        return ""

    # async def save_user_in_anythingllm_and_db(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
    #    """Stores the user first in the AnythingLLM Rest API. and then on local database"""
    # user: AnythingLLMUserDto = self.user_service.save_in_anything_llm(user=user)
    ## Save user in DB with the internal_id from AnythingLLM populated as a result of the Rest API call.
    # user = await self.user_service.save(user=user)
    # return user

    # async def check_user_in_anythingllm_and_update_on_db(self, user: AnythingLLMUserDto) -> AnythingLLMUserDto:
    # We update the user no matter what, to avoid getting the user,
    # inspecting if roles are the same and if they missmatch
    # performing another call to update the user on AnythingLLM; since no matter what the use-case is, we would need
    # to perform at least 1 API call in this use-case, we minimise the number of calls
    # to be only 1 instead of 2 in the worst case scenario.
    # if user.internal_id is None:
    #    raise ValueError("If the user exists in the database it should have an AnythingLLM internal ID.")

    # user = await self.user_service.update(user=user)
    # user = await self.user_service.update_user_in_anything_llm(user=user)
    # return user
