from typing import Dict

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class KeycloakTokenConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KEYCLOAK_ANYTHING_LLM_", enable_decoding=False)

    group_correlations: Dict[str, str]
    # unique ID used for users in the keycloak token.
    id_claim: str
    # username property in the JWT token (preferred_username, for example).
    username_claim: str
    # claim property in the JWT token that holds the groups (groups, for example).
    group_claim: str

    @field_validator("group_correlations", mode="before")
    @classmethod
    def decode_groups(cls, v: str) -> Dict[str, str]:
        # Process a string-based array of key-value pairs using ; and , as separators:
        # expected format of the KEYCLOAK_ANYTING_LLM_GROUP_CORRELATIONS env var is (in one single line)
        # (there is a two line comment here due to compying with linting checks)
        # KEYCLOAK_ANYTING_LLM_GROUP_CORRELATIONS=
        # keycloak_admin,admin;my_other_keycloak_group,manager;other_keycloak_group_default,default
        # Processing logic is:
        # Split by , to get the key->values pairs as a string.
        # For each key->value pair string-based entry, split by ";" to get the value and the pair as different strings.
        return {str(x.split(";")[0]): str(x.split(";")[1]) for x in v.split(",")}
