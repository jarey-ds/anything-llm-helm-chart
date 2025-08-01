from kink import di

from sso_anythingllm_service.config.anything_llm import AnythingLLMConfig
from sso_anythingllm_service.config.keycloak import KeycloakTokenConfig


def setup_di():
    # Exporting configuration into dependency injection context.
    # Keycloak configuration
    keycloak_config = KeycloakTokenConfig()
    # AnythingLLM configuration
    anythingllm_config = AnythingLLMConfig()
    di[KeycloakTokenConfig] = keycloak_config
    di[AnythingLLMConfig] = anythingllm_config

    print("Dependency injection finished.")
