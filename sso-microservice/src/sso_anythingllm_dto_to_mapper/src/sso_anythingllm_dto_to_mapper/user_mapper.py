from kink import inject

from sso_anythingllm_dto.config.keycloak import KeycloakTokenConfig
from sso_anythingllm_dto.user import AnythingLLMUserDto


class AnythingLLMUserDtoToMapper:
    """Maps ModelPropertyInstanceDto to PropertyValueTo for REST API responses."""

    @inject
    def __init__(self, keycloak_config: KeycloakTokenConfig):
        self.keycloak_config = keycloak_config

    def to_target(self, origin: AnythingLLMUserDto) -> dict:
        """Convert AnythingLLMUserDto tio dict based key-values properties.

        Raises:
            ValueError: If properties can't be provided as dict
        """
        return origin.model_dump()

    def from_target(self, target: dict) -> AnythingLLMUserDto:
        """Convert dict based key-values properties to AnythingLLMUserDto."""
        user_dto: AnythingLLMUserDto = AnythingLLMUserDto(
            name=target[self.keycloak_config.username_claim],
            keycloak_id=target[self.keycloak_config.id_claim],
            role=self.keycloak_config.group_correlations[target[self.keycloak_config.group_claim]],
        )
        return user_dto
