from typing import Any, Optional, Protocol


class AnythingLLMRepositoryInterface(Protocol):
    """Rest client interacting with AnythinLLM instance consuming corresponding REST API."""

    async def get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None, auth_token: Optional[str] = None
    ) -> dict[str, Any]:
        """Perform GET request to AnythingLLM API"""
        ...

    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """Perform POST request to AnythingLLM API"""
        ...

    async def delete(
        self, endpoint: str, params: Optional[dict[str, Any]] = None, auth_token: Optional[str] = None
    ) -> dict[str, Any]:
        """Perform DELETE request to AnythingLLM API"""
        ...

    async def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """Perform PUT request to AnythingLLM API"""
        ...

    async def patch(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        auth_token: Optional[str] = None,
    ) -> dict[str, Any]:
        """Perform PATCH request to AnythingLLM API"""
        ...
