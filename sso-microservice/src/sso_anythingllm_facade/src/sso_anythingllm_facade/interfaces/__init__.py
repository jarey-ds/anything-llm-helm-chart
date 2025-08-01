"""Facade interfaces module."""

from artemis_model_catalogue_facade.interfaces.capability_facade_interface import CapabilityFacadeInterface
from artemis_model_catalogue_facade.interfaces.model_instance_facade_interface import ModelInstanceFacadeInterface
from artemis_model_catalogue_facade.interfaces.model_property_type_facade_interface import (
    ModelPropertyTypeFacadeInterface,
)
from artemis_model_catalogue_facade.interfaces.model_template_facade_interface import ModelTemplateFacadeInterface
from artemis_model_catalogue_facade.interfaces.model_type_facade_interface import ModelTypeFacadeInterface
from artemis_model_catalogue_facade.interfaces.owner_type_facade_interface import OwnerTypeFacadeInterface
from artemis_model_catalogue_facade.interfaces.provider_facade_interface import ProviderFacadeInterface
from artemis_model_catalogue_facade.interfaces.provider_model_facade_interface import ProviderModelFacadeInterface

__all__ = [
    "CapabilityFacadeInterface",
    "ModelTemplateFacadeInterface",
    "ModelTypeFacadeInterface",
    "ModelPropertyTypeFacadeInterface",
    "ModelInstanceFacadeInterface",
    "OwnerTypeFacadeInterface",
    "ProviderFacadeInterface",
    "ProviderModelFacadeInterface",
]
