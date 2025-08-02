import asyncio
import logging
from dataclasses import dataclass

from kink import inject
from loguru import logger
from pyctuator.health.health_provider import HealthDetails, HealthProvider, HealthStatus, Status

from sso_anythingllm_dto.config.anything_llm import AnythingLLMConfig
from sso_anythingllm_repository.anything_llm_repository import AnythingLLMRepository
from sso_anythingllm_repository.config import AnythingLLMConfig as RepositoryAnythingLLMConfig
from sso_anythingllm_repository.exceptions import AnythingLLMRepositoryError, AuthenticationError, NetworkError


@dataclass
class ApiHealthDetails(HealthDetails):
    error: str | None = None
    message: str | None = None
    url: str | None = None
    component: str | None = "anythingllm-api"


@dataclass
class ApiHealthStatus(HealthStatus):
    status: Status
    details: ApiHealthDetails


@inject
class AnythingLlmApiHealthMonitor(HealthProvider):
    """Health provider that validates the reachability of the AnythingLLM REST API."""

    def __init__(
        self,
        anythingllm_config: AnythingLLMConfig,
        name: str = "anythingllm-api",
    ) -> None:
        self.name = name
        self.anythingllm_config = anythingllm_config
        self.logger = logging.getLogger(__name__)

    def get_name(self) -> str:
        return self.name

    def is_supported(self) -> bool:
        return True

    def _convert_to_repository_config(self) -> RepositoryAnythingLLMConfig:
        """Convert DTO config to repository config."""
        return RepositoryAnythingLLMConfig(
            base_url=self.anythingllm_config.url,
            api_key=None,  # We don't need API key for auth token endpoint
            timeout=30,
            max_retries=3,
            verify_ssl=self.anythingllm_config.verify_ssl,
        )

    def get_health(self) -> HealthStatus:
        """Check the health of the AnythingLLM REST API by attempting to obtain an auth token."""
        try:
            # Run the async health check in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result = loop.run_until_complete(self._check_api_health())
                return result
            finally:
                loop.close()

        except Exception as e:
            self.logger.error(f"Error checking AnythingLLM API health: {e}")
            return ApiHealthStatus(
                status=Status.DOWN, details=ApiHealthDetails(error=str(e), component="anythingllm-api")
            )

    async def _check_api_health(self) -> HealthStatus:
        """Async method to check the AnythingLLM API health."""
        try:
            # Convert DTO config to repository config
            repo_config = self._convert_to_repository_config()

            # Create repository instance with configuration
            repo = AnythingLLMRepository(config=repo_config)

            async with repo:
                # Test the API by attempting to obtain an auth token
                # This endpoint doesn't require authentication and tests basic connectivity
                credentials = {
                    "username": self.anythingllm_config.admin_user,
                    "password": self.anythingllm_config.admin_password,
                }

                # Call the obtain_auth_token method to test API connectivity
                response = await repo.obtain_auth_token(credentials)
                logger.debug(f"Obtained token is: {response}")

                # If we get here, the API is reachable
                self.logger.debug("AnythingLLM API health check successful")
                return ApiHealthStatus(
                    status=Status.UP,
                    details=ApiHealthDetails(
                        message="AnythingLLM API is reachable",
                        component="anythingllm-api",
                        url=self.anythingllm_config.url,
                    ),
                )

        except AuthenticationError as e:
            # Authentication failed, but API is reachable
            self.logger.warning(f"AnythingLLM API authentication failed: {e}")
            return ApiHealthStatus(
                status=Status.DOWN,
                details=ApiHealthDetails(
                    message="AnythingLLM API is reachable but authentication failed",
                    component="anythingllm-api",
                    url=self.anythingllm_config.url,
                    error=str(e),
                ),
            )

        except NetworkError as e:
            # Network/connection error
            self.logger.error(f"AnythingLLM API network error: {e}")
            error_msg = str(e)

            # Check if it's an SSL certificate error
            if "CERTIFICATE_VERIFY_FAILED" in error_msg or "self-signed certificate" in error_msg:
                error_msg = (
                    f"SSL certificate verification failed. Consider setting ANYTHING_LLM_VERIFY_SSL=false: {error_msg}"
                )

            return ApiHealthStatus(
                status=Status.DOWN,
                details=ApiHealthDetails(
                    message="Network error connecting to AnythingLLM API",
                    component="anythingllm-api",
                    url=self.anythingllm_config.url,
                    error=error_msg,
                ),
            )

        except AnythingLLMRepositoryError as e:
            # Other repository errors
            self.logger.error(f"AnythingLLM API repository error: {e}")
            return ApiHealthStatus(
                status=Status.DOWN,
                details=ApiHealthDetails(
                    message="Error at repository level.",
                    component="anythingllm-api",
                    url=self.anythingllm_config.url,
                    error=str(e),
                ),
            )

        except Exception as e:
            # Unexpected errors
            self.logger.error(f"Unexpected error checking AnythingLLM API health: {e}")
            return ApiHealthStatus(
                status=Status.DOWN,
                details=ApiHealthDetails(
                    message="Unexpected error.",
                    component="anythingllm-api",
                    url=self.anythingllm_config.url,
                    error=str(e),
                ),
            )
