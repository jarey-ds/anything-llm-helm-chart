"""
Unit tests for ApiKeyService.

This test suite verifies that the ApiKeyService correctly:
1. Maps between DTOs and entities
2. Delegates operations to the repository
3. Handles all CRUD operations
"""

from unittest.mock import MagicMock

import pytest

from sso_anythingllm_dto.api_key import ApiKeyDto
from sso_anythingllm_entity.api_key import ApiKey
from sso_anythingllm_repository.interfaces.api_key_repository_interface import ApiKeyRepositoryInterface
from sso_anythingllm_service.api_key_service import ApiKeyService


class TestApiKeyService:
    """Test cases for ApiKeyService."""

    @pytest.fixture
    def mock_api_key_repository(self):
        """Mock API key repository."""
        return MagicMock(spec=ApiKeyRepositoryInterface)

    @pytest.fixture
    def api_key_service(self, mock_api_key_repository):
        """Create ApiKeyService instance with mocked dependencies."""
        return ApiKeyService(mock_api_key_repository)

    @pytest.fixture
    def sample_api_key_dto(self):
        """Create a sample API key DTO for testing."""
        return ApiKeyDto(value="test-api-key-123")

    @pytest.fixture
    def sample_api_key_entity(self):
        """Create a sample API key entity for testing."""
        return ApiKey(value="test-api-key-123")

    @pytest.mark.asyncio
    async def test_get_api_key_by_value_success(
        self, api_key_service, mock_api_key_repository, sample_api_key_entity, sample_api_key_dto
    ):
        """Test successful API key retrieval by value."""
        # Mock repository response
        mock_api_key_repository.get_by_value.return_value = sample_api_key_entity

        # Execute
        result = await api_key_service.get_api_key_by_value("test-api-key-123")

        # Assertions
        assert result.value == sample_api_key_dto.value
        mock_api_key_repository.get_by_value.assert_called_once_with("test-api-key-123")

    @pytest.mark.asyncio
    async def test_get_all_api_keys_success(self, api_key_service, mock_api_key_repository, sample_api_key_entity):
        """Test successful retrieval of all API keys."""
        # Mock repository response
        mock_api_key_repository.get_all_api_keys.return_value = [sample_api_key_entity]

        # Execute
        result = await api_key_service.get_all_api_keys()

        # Assertions
        assert len(result) == 1
        assert result[0].value == sample_api_key_entity.value
        mock_api_key_repository.get_all_api_keys.assert_called_once()

    @pytest.mark.asyncio
    async def test_api_key_exists_true(self, api_key_service, mock_api_key_repository):
        """Test api_key_exists when API key exists."""
        # Mock repository response
        mock_api_key_repository.api_key_exists.return_value = True

        # Execute
        result = await api_key_service.api_key_exists("test-api-key-123")

        # Assertions
        assert result is True
        mock_api_key_repository.api_key_exists.assert_called_once_with("test-api-key-123")

    @pytest.mark.asyncio
    async def test_api_key_exists_false(self, api_key_service, mock_api_key_repository):
        """Test api_key_exists when API key doesn't exist."""
        # Mock repository response
        mock_api_key_repository.api_key_exists.return_value = False

        # Execute
        result = await api_key_service.api_key_exists("test-api-key-123")

        # Assertions
        assert result is False
        mock_api_key_repository.api_key_exists.assert_called_once_with("test-api-key-123")

    @pytest.mark.asyncio
    async def test_count_api_keys_success(self, api_key_service, mock_api_key_repository):
        """Test successful counting of API keys."""
        # Mock repository response
        mock_api_key_repository.count_api_keys.return_value = 5

        # Execute
        result = await api_key_service.count_api_keys()

        # Assertions
        assert result == 5
        mock_api_key_repository.count_api_keys.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_api_key_success(
        self, api_key_service, mock_api_key_repository, sample_api_key_dto, sample_api_key_entity
    ):
        """Test successful API key creation."""
        # Mock repository response
        mock_api_key_repository.save.return_value = sample_api_key_entity

        # Execute
        result = await api_key_service.save(sample_api_key_dto)

        # Assertions
        assert result.value == sample_api_key_dto.value
        mock_api_key_repository.save.assert_called_once()
        # Verify the mapper was used correctly
        saved_entity = mock_api_key_repository.save.call_args[0][0]
        assert isinstance(saved_entity, ApiKey)
        assert saved_entity.value == sample_api_key_dto.value

    @pytest.mark.asyncio
    async def test_update_api_key_success(
        self, api_key_service, mock_api_key_repository, sample_api_key_dto, sample_api_key_entity
    ):
        """Test successful API key update."""
        # Mock repository response
        mock_api_key_repository.update.return_value = sample_api_key_entity

        # Execute
        result = await api_key_service.update(sample_api_key_dto)

        # Assertions
        assert result.value == sample_api_key_dto.value
        mock_api_key_repository.update.assert_called_once()
        # Verify the mapper was used correctly
        updated_entity = mock_api_key_repository.update.call_args[0][0]
        assert isinstance(updated_entity, ApiKey)
        assert updated_entity.value == sample_api_key_dto.value

    @pytest.mark.asyncio
    async def test_delete_by_value_success(self, api_key_service, mock_api_key_repository):
        """Test successful API key deletion by value."""
        # Mock repository response
        mock_api_key_repository.delete_by_value.return_value = None

        # Execute
        await api_key_service.delete_by_value("test-api-key-123")

        # Assertions
        mock_api_key_repository.delete_by_value.assert_called_once_with("test-api-key-123")

    @pytest.mark.asyncio
    async def test_legacy_create_method(
        self, api_key_service, mock_api_key_repository, sample_api_key_dto, sample_api_key_entity
    ):
        """Test legacy create method."""
        # Mock repository response
        mock_api_key_repository.save.return_value = sample_api_key_entity

        # Execute
        result = await api_key_service.create(sample_api_key_dto)

        # Assertions
        assert result.value == sample_api_key_dto.value
        mock_api_key_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_legacy_delete_method(self, api_key_service, mock_api_key_repository, sample_api_key_dto):
        """Test legacy delete method."""
        # Mock repository response
        mock_api_key_repository.delete_by_value.return_value = None

        # Execute
        await api_key_service.delete(sample_api_key_dto)

        # Assertions
        mock_api_key_repository.delete_by_value.assert_called_once_with(sample_api_key_dto.value)

    @pytest.mark.asyncio
    async def test_legacy_get_api_keys_method(self, api_key_service, mock_api_key_repository, sample_api_key_entity):
        """Test legacy get_api_keys method."""
        # Mock repository response
        mock_api_key_repository.get_all_api_keys.return_value = [sample_api_key_entity]

        # Execute
        result = await api_key_service.get_api_keys()

        # Assertions
        assert len(result) == 1
        assert result[0].value == sample_api_key_entity.value
        mock_api_key_repository.get_all_api_keys.assert_called_once()
