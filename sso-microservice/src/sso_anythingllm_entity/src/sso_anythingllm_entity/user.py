# Core libraries
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "anythingllm_user"  # type: ignore[assignment]

    keycloak_id: str = Field(
        primary_key=True, default=None, description="Unique identifier of an user in the Keycloak system."
    )
    internal_id: int = Field(default=None, description="User's AnythingLLM internal ID.")
    name: str = Field(default=None, description="User's name")
    role: str = Field(description="AnythingLLM user's application role (admin|manager|default)")
