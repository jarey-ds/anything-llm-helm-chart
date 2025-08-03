"""
Custom exceptions for AnythingLLM repository operations.
"""


class AnythingLLMRepositoryError(Exception):
    """Base exception for AnythingLLM repository errors."""

    pass


class NetworkError(AnythingLLMRepositoryError):
    """Exception raised for network-related errors."""

    pass


class AuthenticationError(AnythingLLMRepositoryError):
    """Exception raised for authentication errors."""

    pass


class ValidationError(AnythingLLMRepositoryError):
    """Exception raised for data validation errors."""

    pass


class ConfigurationError(AnythingLLMRepositoryError):
    """Exception raised for configuration errors."""

    pass
