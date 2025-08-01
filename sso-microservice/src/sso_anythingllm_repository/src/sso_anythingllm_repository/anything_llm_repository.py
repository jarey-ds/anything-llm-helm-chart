import asyncio
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from httpx import ConnectError, RequestError, TimeoutException

from .config import AnythingLLMConfig
from .exceptions import AnythingLLMRepositoryError, AuthenticationError, NetworkError


class AnythingLLMRepository:
    """
    REST API client for AnythingLLM with support for GET, POST, DELETE, PUT, and PATCH methods.
    This class provides a comprehensive interface for interacting with the AnythingLLM REST API
    with configurable arguments such as URL, headers, timeouts, and retry logic.
    """

    def __init__(self, config: AnythingLLMConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url, headers=self.config.get_headers(), timeout=self.config.timeout
            )

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _build_url(self, endpoint: str) -> str:
        return urljoin(self.config.base_url, endpoint.lstrip("/"))

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        await self._ensure_client()
        url = self._build_url(endpoint)
        request_kwargs = {"params": params, **kwargs}
        if data is not None:
            request_kwargs["data"] = data
        if json_data is not None:
            request_kwargs["json"] = json_data

        for attempt in range(self.config.max_retries + 1):
            try:
                self.logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                response = await self._client.request(method, url, **request_kwargs)

                if response.status_code == 200:
                    return response.json() if response.content else {}
                elif response.status_code == 201:
                    return response.json() if response.content else {"status": "created"}
                elif response.status_code == 204:
                    return {"status": "no_content"}
                elif response.status_code == 401:
                    raise AuthenticationError(f"Authentication failed: {response.text}")
                elif response.status_code == 403:
                    raise AuthenticationError(f"Access forbidden: {response.text}")
                elif response.status_code == 404:
                    raise AnythingLLMRepositoryError(f"Resource not found: {response.text}")
                elif response.status_code >= 500:
                    if attempt < self.config.max_retries:
                        wait_time = 2**attempt
                        self.logger.warning(f"Server error {response.status_code}, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise NetworkError(f"Server error after {self.config.max_retries} retries: {response.text}")
                else:
                    raise AnythingLLMRepositoryError(f"HTTP {response.status_code}: {response.text}")
            except TimeoutException as e:
                if attempt < self.config.max_retries:
                    wait_time = 2**attempt
                    self.logger.warning(f"Timeout, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise NetworkError(f"Request timeout after {self.config.max_retries} retries") from e
            except ConnectError as e:
                raise NetworkError(f"Connection error: {e}") from e
            except RequestError as e:
                raise NetworkError(f"Request error: {e}") from e
        raise NetworkError(f"Request failed after {self.config.max_retries} retries")

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._make_request("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._make_request("POST", endpoint, data=data, json_data=json_data)

    async def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return await self._make_request("DELETE", endpoint, params=params)

    async def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._make_request("PUT", endpoint, data=data, json_data=json_data)

    async def patch(
        self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self._make_request("PATCH", endpoint, data=data, json_data=json_data)

    async def get_workspaces(self) -> Dict[str, Any]:
        return await self.get("/api/v1/workspaces")

    async def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        return await self.get(f"/api/v1/workspaces/{workspace_id}")

    async def create_workspace(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post("/api/v1/workspaces", json_data=workspace_data)

    async def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        return await self.delete(f"/api/v1/workspaces/{workspace_id}")

    async def get_documents(self, workspace_id: str) -> Dict[str, Any]:
        return await self.get(f"/api/v1/workspaces/{workspace_id}/documents")

    async def upload_document(self, workspace_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post(f"/api/v1/workspaces/{workspace_id}/documents", json_data=document_data)

    # ----------------------------  Especific methods to use in bussines logic ---------------------------------------

    async def obtain_auth_token(self, credentials_data: Dict[str, str]) -> Dict[str, Any]:
        return await self.post("/api/request-token", json_data=credentials_data)

    async def create_api_key(self) -> Dict[str, Any]:
        return await self.post("/api/admin/generate-api-key")

    async def create_user(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        return await self.post("/api/v1/admin/users/new", json_data=user_data)

    async def update_user(self, user_id: int, user_data: Dict[str, str]) -> Dict[str, Any]:
        return await self.post(f"/api/v1/admin/users/{user_id}", json_data=user_data)

    async def delete_user(
        self,
        user_id: int,
    ) -> Dict[str, Any]:
        return await self.delete(f"/api/v1/admin/users/{user_id}")

    async def issue_auth_token(self, user_id: int) -> Dict[str, Any]:
        return await self.get(f"/api/v1/users/{user_id}/issue-auth-token")
