from typing import Any, Dict, Optional, Protocol


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

    async def issue_auth_token(self, user_id: int, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Generate new one-time access URL"""
        ...

    async def create_api_key(self, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Create a new API Token"""
        ...

    async def obtain_auth_token(
        self, credentials_data: Dict[str, str], auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtain the auth token for a given user"""
        ...

    async def create_user(self, user_data: Dict[str, str], auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new user in AnythingLLM."""
        ...

    async def update_user(
        self, user_id: int, user_data: Dict[str, Any], auth_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates a given user in AnythingLLM end, using the Rest API."""
        ...
