from pydantic import BaseModel, Field


class KeycloakUserDto(BaseModel):
    id: str
    name: str
    groups: list[str]


class AnythingLLMUserDto(BaseModel):
    keycloak_id: str = Field(description="Unique identifier of an user in the Keycloak system.")
    internal_id: int | None = Field(default=None, description="User's AnythingLLM internal ID.")
    name: str = Field(description="User's name")
    role: str = Field(description="AnythingLLM user's application role (admin|manager|default)")
