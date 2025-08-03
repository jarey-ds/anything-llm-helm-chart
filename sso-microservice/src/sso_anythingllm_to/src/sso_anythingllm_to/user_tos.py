"""This module contains the Model related transport objects"""

from pydantic import BaseModel


class KeycloakUserTo(BaseModel):
    """Transport object for wrapping information coming from Keycloak JWT token."""

    username: str
    primary_key: str
    groups: list[str]
