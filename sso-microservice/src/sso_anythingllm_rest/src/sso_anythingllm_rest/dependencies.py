"""Dependencies for REST endpoints."""

from typing import Generic, Type, TypeVar

from kink import di

T = TypeVar("T")


class LazySingleton(Generic[T]):
    """
    Lazy initialization wrapper for DI singletons to handle import order issues.
    Usage:
        provider_facade = LazySingleton(ProviderFacade)
        # Use provider_facade as if it were the actual ProviderFacade instance
    """

    def __init__(self, service_type: Type[T]):
        self._service_type = service_type
        self._instance: T | None = None

    def __getattr__(self, name: str):
        if self._instance is None:
            self._instance = di[self._service_type]
        return getattr(self._instance, name)

    def __getitem__(self, item):
        """Support subscript access if the wrapped object supports it."""
        if self._instance is None:
            self._instance = di[self._service_type]
        return self._instance[item]

    def __call__(self, *args, **kwargs):
        """Support callable objects."""
        if self._instance is None:
            self._instance = di[self._service_type]
        return self._instance(*args, **kwargs)

    def __repr__(self):
        return f"LazySingleton({self._service_type.__name__})"
