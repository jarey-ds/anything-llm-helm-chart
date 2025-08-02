"""
SSO AnythingLLM Repository

A comprehensive async REST API client for AnythingLLM with support for GET, POST, DELETE, PUT, and PATCH methods.
"""

from sso_anythingllm_repository.anything_llm_repository import AnythingLLMRepository
from sso_anythingllm_repository.config import AnythingLLMConfig, AsyncPostgresConf
from sso_anythingllm_repository.exceptions import (
    AnythingLLMRepositoryError,
    AuthenticationError,
    ConfigurationError,
    NetworkError,
    ValidationError,
)
from sso_anythingllm_repository.interfaces import (
    AnythingLLMRepositoryInterface,
    ApiKeyRepositoryInterface,
    UserRepositoryInterface,
)

__all__ = [
    "AnythingLLMRepository",
    "AnythingLLMConfig",
    "AsyncPostgresConf",
    "AnythingLLMRepositoryError",
    "NetworkError",
    "AuthenticationError",
    "ValidationError",
    "ConfigurationError",
    "UserRepositoryInterface",
    "AnythingLLMRepositoryInterface",
    "ApiKeyRepositoryInterface",
]

__version__ = "1.0.0"
