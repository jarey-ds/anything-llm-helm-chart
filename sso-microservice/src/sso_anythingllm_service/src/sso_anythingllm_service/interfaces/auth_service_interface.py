from typing import Protocol


class AuthServiceInterface(Protocol):
    """Interface for the authentication logic against AnythingLLM."""

    async def obtain_auth_token_for_admin(self) -> str:
        """Obtain the auth token for a given user"""
        ...
