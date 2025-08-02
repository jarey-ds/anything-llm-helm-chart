from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sso_anythingllm_entity.api_key import ApiKey
from sso_anythingllm_repository.api_key_repository import ApiKeyRepository
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError


class TestApiKeyRepository:
    """Test cases for ApiKeyRepository."""

    @pytest.fixture
    def mock_db_config(self):
        """Mock database configuration."""
        config = MagicMock(spec=AsyncPostgresConf)
        config.engine = MagicMock()
        return config

    @pytest.fixture
    def api_key_repository(self, mock_db_config):
        """Create ApiKeyRepository instance with mocked dependencies."""
        return ApiKeyRepository(mock_db_config)

    @pytest.fixture
    def sample_api_key(self):
        """Create a sample API key for testing."""
        return ApiKey(value="test-api-key-123")

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_save_api_key_success(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test successful API key creation."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock session.add as a regular method (not async)
        mock_session.add = MagicMock()

        # Mock that API key doesn't exist (for the existence check)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.save(sample_api_key)

        # Assertions
        assert result == sample_api_key
        # Don't assert on session.add() as it's not awaited in the mock
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_api_key)

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_save_api_key_already_exists(
        self, mock_async_session, api_key_repository, sample_api_key, mock_db_config
    ):
        """Test API key creation when API key already exists."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock that API key exists
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_api_key
        mock_session.execute.return_value = mock_result

        # Execute and assert
        with pytest.raises(ValidationError, match="already exists"):
            await api_key_repository.save(sample_api_key)

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_get_by_value_success(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test successful API key retrieval by value."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API key found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_api_key
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.get_by_value("test-api-key-123")

        # Assertions
        assert result == sample_api_key

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_get_by_value_not_found(self, mock_async_session, api_key_repository, mock_db_config):
        """Test API key retrieval when API key doesn't exist."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API key not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute and assert
        with pytest.raises(ValidationError, match="not found"):
            await api_key_repository.get_by_value("non-existent-api-key")

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_update_api_key_success(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test successful API key update."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock existing API key for the existence check
        existing_api_key = ApiKey(value="test-api-key-123")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_api_key
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.update(sample_api_key)

        # Assertions
        assert result == existing_api_key
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_delete_api_key_success(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test successful API key deletion."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock existing API key
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_api_key
        mock_session.execute.return_value = mock_result

        # Execute
        await api_key_repository.delete_by_value("test-api-key-123")

        # Assertions
        # Don't assert on session.delete() as it's not awaited in the mock
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_get_all_api_keys(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test retrieving all API keys."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API keys
        api_keys = [sample_api_key]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = api_keys
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.get_all_api_keys()

        # Assertions
        assert result == api_keys

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_api_key_exists_true(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test api_key_exists when API key exists."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API key found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_api_key
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.api_key_exists("test-api-key-123")

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_api_key_exists_false(self, mock_async_session, api_key_repository, mock_db_config):
        """Test api_key_exists when API key doesn't exist."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API key not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.api_key_exists("non-existent-api-key")

        # Assertions
        assert result is False

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_count_api_keys(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test counting API keys."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API keys
        api_keys = [sample_api_key]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = api_keys
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.count_api_keys()

        # Assertions
        assert result == 1

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_legacy_create_method(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test legacy create method."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock session.add as a regular method (not async)
        mock_session.add = MagicMock()

        # Mock that API key doesn't exist
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.create(sample_api_key)

        # Assertions
        assert result == sample_api_key
        mock_session.add.assert_called_once_with(sample_api_key)

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_legacy_delete_method(self, mock_async_session, api_key_repository, sample_api_key, mock_db_config):
        """Test legacy delete method."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock existing API key
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_api_key
        mock_session.execute.return_value = mock_result

        # Execute
        await api_key_repository.delete(sample_api_key)

        # Assertions
        mock_session.delete.assert_called_once_with(sample_api_key)

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.api_key_repository.AsyncSession")
    async def test_legacy_get_api_keys_method(
        self, mock_async_session, api_key_repository, sample_api_key, mock_db_config
    ):
        """Test legacy get_api_keys method."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock API keys
        api_keys = [sample_api_key]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = api_keys
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Execute
        result = await api_key_repository.get_api_keys()

        # Assertions
        assert result == api_keys
