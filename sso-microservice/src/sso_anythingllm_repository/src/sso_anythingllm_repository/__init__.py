"""
SSO AnythingLLM Repository

A comprehensive async REST API client for AnythingLLM with support for GET, POST, DELETE, PUT, and PATCH methods.
"""

from .anything_llm_repository import AnythingLLMRepository
from .config import AnythingLLMConfig, AsyncPostgresConf
from .exceptions import (
    AnythingLLMRepositoryError,
    AuthenticationError,
    ConfigurationError,
    NetworkError,
    ValidationError,
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
]

__version__ = "1.0.0"
