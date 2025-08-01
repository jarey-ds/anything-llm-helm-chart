"""Exception classes for the facade layer."""

from core_exceptions.core import BaseGenericException


class FacadeException(BaseGenericException):
    """Base exception for facade-related errors."""

    pass


class OrchestrationException(FacadeException):
    """Exception raised when orchestration of multiple services fails."""

    pass


class InvalidWorkflowException(FacadeException):
    """Exception raised when a requested workflow is invalid or cannot be completed."""

    pass
