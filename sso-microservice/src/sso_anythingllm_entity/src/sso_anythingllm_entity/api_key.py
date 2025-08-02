# Core libraries
from sqlmodel import Field, SQLModel


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_key"  # type: ignore[assignment]

    value: str = Field(
        primary_key=True, default=None, description="Unique identifier of an user in the Keycloak system."
    )
