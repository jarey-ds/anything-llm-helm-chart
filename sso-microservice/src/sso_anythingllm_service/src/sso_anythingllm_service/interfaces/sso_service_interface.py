"""Capability service interface using Protocol."""

from typing import Protocol


class SSOServiceInterface(Protocol):
    """Interface for capability service operations."""

    async def get_sso_url_for_user(self) -> str:
        """Obtain the SSO single use URL for the user, via AnythingLLM's Rest API"""
        ...
