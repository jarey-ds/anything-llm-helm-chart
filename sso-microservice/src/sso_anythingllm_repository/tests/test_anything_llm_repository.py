from unittest.mock import MagicMock, patch

import httpx
import pytest
from httpx import ConnectError, TimeoutException

from sso_anythingllm_repository.anything_llm_repository import AnythingLLMRepository
from sso_anythingllm_repository.config import AnythingLLMConfig
from sso_anythingllm_repository.exceptions import AnythingLLMRepositoryError, AuthenticationError, NetworkError


class TestAnythingLLMRepository:
    @pytest.fixture
    def config(self):
        return AnythingLLMConfig(
            base_url="https://api.anythingllm.com",
            api_key="test-api-key",
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def repository(self, config):
        return AnythingLLMRepository(config)

    @pytest.mark.asyncio
    async def test_init(self, config):
        """Test repository initialization"""
        repo = AnythingLLMRepository(config)
        assert repo.config == config
        assert repo._client is None

    @pytest.mark.asyncio
    async def test_context_manager(self, config):
        """Test async context manager"""
        async with AnythingLLMRepository(config) as repo:
            assert repo._client is not None
            assert isinstance(repo._client, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_build_url(self, repository):
        """Test URL building"""
        url = repository._build_url("/api/v1/workspaces")
        assert url == "https://api.anythingllm.com/api/v1/workspaces"

        url = repository._build_url("api/v1/workspaces")
        assert url == "https://api.anythingllm.com/api/v1/workspaces"

    @pytest.mark.asyncio
    async def test_get_auth_headers_with_api_key(self, repository):
        """Test auth headers with API key from config"""
        headers = repository._get_auth_headers()
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_auth_headers_with_token(self, repository):
        """Test auth headers with provided token"""
        headers = repository._get_auth_headers("jwt-token-123")
        assert headers["Authorization"] == "Bearer jwt-token-123"
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_get_auth_headers_no_auth(self, config):
        """Test auth headers without API key or token"""
        config.api_key = None
        repo = AnythingLLMRepository(config)
        headers = repo._get_auth_headers()
        assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_successful_get_request(self, repository):
        """Test successful GET request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"workspaces": []}
        mock_response.content = b'{"workspaces": []}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            result = await repository.get("/api/v1/workspaces")
            assert result == {"workspaces": []}

    @pytest.mark.asyncio
    async def test_successful_get_request_with_token(self, repository):
        """Test successful GET request with auth token"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"workspaces": []}
        mock_response.content = b'{"workspaces": []}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response) as mock_request:
            result = await repository.get("/api/v1/workspaces", auth_token="jwt-token-123")
            assert result == {"workspaces": []}
            # Verify the request was made with the correct auth header
            call_args = mock_request.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer jwt-token-123"

    @pytest.mark.asyncio
    async def test_successful_post_request(self, repository):
        """Test successful POST request"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123", "name": "Test Workspace"}
        mock_response.content = b'{"id": "123", "name": "Test Workspace"}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            result = await repository.post("/api/v1/workspaces", json_data={"name": "Test Workspace"})
            assert result == {"id": "123", "name": "Test Workspace"}

    @pytest.mark.asyncio
    async def test_successful_post_request_with_token(self, repository):
        """Test successful POST request with auth token"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123", "name": "Test Workspace"}
        mock_response.content = b'{"id": "123", "name": "Test Workspace"}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response) as mock_request:
            result = await repository.post(
                "/api/v1/workspaces", json_data={"name": "Test Workspace"}, auth_token="jwt-token-123"
            )
            assert result == {"id": "123", "name": "Test Workspace"}
            # Verify the request was made with the correct auth header
            call_args = mock_request.call_args
            assert call_args[1]["headers"]["Authorization"] == "Bearer jwt-token-123"

    @pytest.mark.asyncio
    async def test_successful_delete_request(self, repository):
        """Test successful DELETE request"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.content = b""

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            result = await repository.delete("/api/v1/workspaces/123")
            assert result == {"status": "no_content"}

    @pytest.mark.asyncio
    async def test_authentication_error(self, repository):
        """Test authentication error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            with pytest.raises(AuthenticationError, match="Authentication failed"):
                await repository.get("/api/v1/workspaces")

    @pytest.mark.asyncio
    async def test_not_found_error(self, repository):
        """Test not found error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            with pytest.raises(AnythingLLMRepositoryError, match="Resource not found"):
                await repository.get("/api/v1/workspaces/999")

    @pytest.mark.asyncio
    async def test_server_error_with_retry(self, repository):
        """Test server error with retry logic"""
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500
        mock_response_500.text = "Internal Server Error"

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"workspaces": []}
        mock_response_200.content = b'{"workspaces": []}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", side_effect=[mock_response_500, mock_response_200]):
            with patch("asyncio.sleep", return_value=None):  # Mock sleep to speed up test
                result = await repository.get("/api/v1/workspaces")
                assert result == {"workspaces": []}

    @pytest.mark.asyncio
    async def test_timeout_error_with_retry(self, repository):
        """Test timeout error with retry logic"""
        await repository._ensure_client()
        with patch.object(repository._client, "request", side_effect=TimeoutException("Request timeout")):
            with patch("asyncio.sleep", return_value=None):  # Mock sleep to speed up test
                with pytest.raises(NetworkError, match="Request timeout"):
                    await repository.get("/api/v1/workspaces")

    @pytest.mark.asyncio
    async def test_connection_error(self, repository):
        """Test connection error handling"""
        await repository._ensure_client()
        with patch.object(repository._client, "request", side_effect=ConnectError("Connection failed")):
            with pytest.raises(NetworkError, match="Connection error"):
                await repository.get("/api/v1/workspaces")

    @pytest.mark.asyncio
    async def test_convenience_methods(self, repository):
        """Test convenience methods"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"workspaces": []}
        mock_response.content = b'{"workspaces": []}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            # Test get_workspaces
            result = await repository.get_workspaces()
            assert result == {"workspaces": []}

            # Test get_workspace
            result = await repository.get_workspace("123")
            assert result == {"workspaces": []}

            # Test create_workspace
            result = await repository.create_workspace({"name": "Test"})
            assert result == {"workspaces": []}

            # Test delete_workspace
            result = await repository.delete_workspace("123")
            assert result == {"workspaces": []}

            # Test get_documents
            result = await repository.get_documents("123")
            assert result == {"workspaces": []}

            # Test upload_document
            result = await repository.upload_document("123", {"name": "test.pdf"})
            assert result == {"workspaces": []}

    @pytest.mark.asyncio
    async def test_business_logic_methods(self, repository):
        """Test business logic methods"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_response.content = b'{"success": true}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            # Test obtain_auth_token
            result = await repository.obtain_auth_token({"username": "test", "password": "test"})
            assert result == {"success": True}

            # Test create_api_key
            result = await repository.create_api_key()
            assert result == {"success": True}

            # Test create_user
            result = await repository.create_user({"username": "test", "email": "test@example.com"})
            assert result == {"success": True}

            # Test update_user
            result = await repository.update_user(1, {"username": "updated"})
            assert result == {"success": True}

            # Test delete_user
            result = await repository.delete_user(1)
            assert result == {"success": True}

            # Test issue_auth_token
            result = await repository.issue_auth_token(1)
            assert result == {"success": True}

    @pytest.mark.asyncio
    async def test_close_client(self, repository):
        """Test client closing"""
        await repository._ensure_client()
        assert repository._client is not None
        await repository.close()
        assert repository._client is None

    @pytest.mark.asyncio
    async def test_put_request(self, repository):
        """Test PUT request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}
        mock_response.content = b'{"updated": true}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            result = await repository.put("/api/v1/workspaces/123", json_data={"name": "Updated"})
            assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_patch_request(self, repository):
        """Test PATCH request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"patched": True}
        mock_response.content = b'{"patched": true}'

        await repository._ensure_client()
        with patch.object(repository._client, "request", return_value=mock_response):
            result = await repository.patch("/api/v1/workspaces/123", json_data={"name": "Patched"})
            assert result == {"patched": True}


class TestAnythingLLMConfig:
    """Test cases for AnythingLLMConfig"""

    def test_config_creation(self):
        """Test configuration creation"""
        config = AnythingLLMConfig(base_url="http://localhost:3001", api_key="test-key", timeout=60, max_retries=5)

        assert config.base_url == "http://localhost:3001"
        assert config.api_key == "test-key"
        assert config.timeout == 60
        assert config.max_retries == 5

    def test_get_headers_with_api_key(self):
        """Test header generation with API key"""
        config = AnythingLLMConfig(base_url="http://localhost:3001", api_key="test-key")

        headers = config.get_headers()
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"

    def test_get_headers_without_api_key(self):
        """Test header generation without API key"""
        config = AnythingLLMConfig(base_url="http://localhost:3001")

        headers = config.get_headers()
        assert "Authorization" not in headers
        assert headers["Content-Type"] == "application/json"

    def test_get_headers_with_custom_headers(self):
        """Test header generation with custom headers"""
        config = AnythingLLMConfig(
            base_url="http://localhost:3001", api_key="test-key", headers={"X-Custom-Header": "custom-value"}
        )

        headers = config.get_headers()
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"
        assert headers["X-Custom-Header"] == "custom-value"
