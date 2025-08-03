"""Constants and enums for entity models."""

from enum import StrEnum


class AnythingLLMRoleType(StrEnum):
    """Enumeration of supported model property types.

    These types define the data type of a property and are used
    to determine UI controls and validation rules.
    """

    DEFAULT = "default"
    MANAGER = "manager"
    ADMIN = "admin"
