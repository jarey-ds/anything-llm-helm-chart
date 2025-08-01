from artemis_model_catalogue_dto.model import (
    ModelPropertyInstanceDto,
)
from artemis_model_catalogue_to.model_tos import (
    PropertyValueTo,
)
from typing_extensions import override


class AnythingLLMU:
    """Maps ModelPropertyInstanceDto to PropertyValueTo for REST API responses."""

    @override
    def to_target(self, origin: ModelPropertyInstanceDto) -> PropertyValueTo:
        """Convert ModelPropertyInstanceDto to PropertyValueTo.

        Raises:
            ValueError: If property template is not available in the DTO
        """
        if not origin.model_property_template:
            raise ValueError(f"Property template is required but not found for property instance {origin.id}")

        template = origin.model_property_template
        return PropertyValueTo(
            key=template.key,
            value=origin.value,
            label=template.label,
            property_type=template.property_type,
            required=template.required,
        )

    @override
    def from_target(self, target: PropertyValueTo) -> ModelPropertyInstanceDto:
        """Not implemented - we don't convert back from TO to DTO."""
        raise NotImplementedError("Conversion from PropertyValueTo to ModelPropertyInstanceDto is not supported")
