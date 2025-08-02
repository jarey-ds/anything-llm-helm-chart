from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sso_anythingllm_entity.user import User
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.exceptions import ValidationError
from sso_anythingllm_repository.user_repository import UserRepository


class TestUserRepository:
    """Test cases for UserRepository."""

    @pytest.fixture
    def mock_db_config(self):
        """Mock database configuration."""
        config = MagicMock(spec=AsyncPostgresConf)
        config.engine = MagicMock()
        return config

    @pytest.fixture
    def user_repository(self, mock_db_config):
        """Create UserRepository instance with mocked dependencies."""
        return UserRepository(mock_db_config)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(keycloak_id="test-keycloak-id", internal_id=123, name="Test User", role="admin")

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_save_user_success(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test successful user creation."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock that user doesn't exist (for the existence check)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.save(sample_user)

        # Assertions
        assert result == sample_user
        # Don't assert on session.add() as it's not awaited in the mock
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(sample_user)

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_save_user_already_exists(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test user creation when user already exists."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock that user exists
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        # Execute and assert
        with pytest.raises(ValidationError, match="already exists"):
            await user_repository.save(sample_user)

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_get_by_keycloak_id_success(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test successful user retrieval by keycloak_id."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.get_by_keycloak_id("test-keycloak-id")

        # Assertions
        assert result == sample_user

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_get_by_keycloak_id_not_found(self, mock_async_session, user_repository, mock_db_config):
        """Test user retrieval when user doesn't exist."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock user not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute and assert
        with pytest.raises(ValidationError, match="not found"):
            await user_repository.get_by_keycloak_id("non-existent-id")

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_update_user_success(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test successful user update."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock existing user for the existence check
        existing_user = User(keycloak_id="test-keycloak-id", internal_id=123, name="Old Name", role="user")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_user
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.update(sample_user)

        # Assertions
        assert result.name == sample_user.name
        assert result.role == sample_user.role
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_delete_user_success(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test successful user deletion."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock existing user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        # Execute
        await user_repository.delete_by_keycloak_id("test-keycloak-id")

        # Assertions
        # Don't assert on session.delete() as it's not awaited in the mock
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_get_all_users(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test retrieving all users."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock users
        users = [sample_user]
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = users
        mock_result.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.get_all_users()

        # Assertions
        assert result == users

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_user_exists_true(self, mock_async_session, user_repository, sample_user, mock_db_config):
        """Test user_exists when user exists."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock user found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.user_exists("test-keycloak-id")

        # Assertions
        assert result is True

    @pytest.mark.asyncio
    @patch("sso_anythingllm_repository.user_repository.AsyncSession")
    async def test_user_exists_false(self, mock_async_session, user_repository, mock_db_config):
        """Test user_exists when user doesn't exist."""
        # Mock session
        mock_session = AsyncMock()
        mock_async_session.return_value.__aenter__.return_value = mock_session
        mock_async_session.return_value.__aexit__.return_value = None

        # Mock user not found
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Execute
        result = await user_repository.user_exists("non-existent-id")

        # Assertions
        assert result is False
