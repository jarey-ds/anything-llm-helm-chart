"""Tests for Model Instance mappers"""

import uuid

import pytest
from artemis_model_catalogue_dto.model import (
    ModelInstanceDto,
    ModelPropertyInstanceDto,
    ModelPropertyTemplateDto,
    ModelTemplateDto,
)
from artemis_model_catalogue_dto_to_mapper.model_instance_mapper import (
    ModelInstanceCreateToToModelInstanceDtoMapper,
    ModelInstanceDtoToModelInstanceToMapper,
    ModelPropertyInstanceDtoToPropertyValueToMapper,
)
from artemis_model_catalogue_entity.enums import ModelPropertyType
from artemis_model_catalogue_to.model_tos import (
    ModelInstanceCreateTo,
    PropertyValueTo,
)


class TestModelPropertyInstanceDtoToPropertyValueToMapper:
    """Test ModelPropertyInstanceDto to PropertyValueTo mapping"""

    def test_with_property_template(self):
        """Test mapping with property template provided"""
        mapper = ModelPropertyInstanceDtoToPropertyValueToMapper()

        # Create property template
        template = ModelPropertyTemplateDto(
            id=uuid.uuid4(),
            key="temperature",
            label="Temperature",
            property_type=ModelPropertyType.NUMBER,
            required=True,
            default_value="0.7",
            model_template_id=uuid.uuid4(),
            model_property_type_id=uuid.uuid4(),
        )

        # Create property instance with template
        instance_dto = ModelPropertyInstanceDto(
            id=uuid.uuid4(),
            value="0.9",
            model_instance_id=uuid.uuid4(),
            model_property_template_id=template.id,
            model_property_template=template,
        )

        result = mapper.to_target(instance_dto)

        assert isinstance(result, PropertyValueTo)
        assert result.key == "temperature"
        assert result.value == "0.9"
        assert result.label == "Temperature"
        assert result.property_type == ModelPropertyType.NUMBER
        assert result.required is True

    def test_without_property_template(self):
        """Test mapping without property template raises error"""
        mapper = ModelPropertyInstanceDtoToPropertyValueToMapper()

        instance_dto = ModelPropertyInstanceDto(
            id=uuid.uuid4(),
            value="test_value",
            model_instance_id=uuid.uuid4(),
            model_property_template_id=uuid.uuid4(),
        )

        with pytest.raises(ValueError, match="Property template is required but not found"):
            mapper.to_target(instance_dto)

    def test_from_target_not_implemented(self):
        """Test that from_target raises NotImplementedError"""
        mapper = ModelPropertyInstanceDtoToPropertyValueToMapper()

        property_value = PropertyValueTo(
            key="test",
            value="value",
            label="Test",
            property_type=ModelPropertyType.TEXT,
            required=False,
        )

        with pytest.raises(NotImplementedError):
            mapper.from_target(property_value)


class TestModelInstanceDtoToModelInstanceToMapper:
    """Test ModelInstanceDto to ModelInstanceTo mapping"""

    def test_basic_mapping(self):
        """Test basic mapping without properties"""
        mapper = ModelInstanceDtoToModelInstanceToMapper()

        instance_dto = ModelInstanceDto(
            id=uuid.uuid4(),
            name="Test Instance",
            model_template_id=uuid.uuid4(),
        )

        result = mapper.to_target(instance_dto)

        assert result.id == instance_dto.id
        assert result.name == "Test Instance"
        assert result.model_template_id == instance_dto.model_template_id
        assert result.template_name == "Unknown Template"
        assert result.properties == []

    def test_with_template_and_properties(self):
        """Test mapping with template and property instances"""
        mapper = ModelInstanceDtoToModelInstanceToMapper()

        # Create template with properties
        template = ModelTemplateDto(
            id=uuid.uuid4(),
            name="GPT-4 Template",
            description="Template for GPT-4",
            type_id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            model_property_templates=[
                ModelPropertyTemplateDto(
                    id=uuid.uuid4(),
                    key="temperature",
                    label="Temperature",
                    property_type=ModelPropertyType.NUMBER,
                    required=True,
                    default_value="0.7",
                    model_template_id=uuid.uuid4(),
                    model_property_type_id=uuid.uuid4(),
                ),
                ModelPropertyTemplateDto(
                    id=uuid.uuid4(),
                    key="max_tokens",
                    label="Max Tokens",
                    property_type=ModelPropertyType.NUMBER,
                    required=False,
                    default_value="2048",
                    model_template_id=uuid.uuid4(),
                    model_property_type_id=uuid.uuid4(),
                ),
            ],
        )

        # Create property instances
        prop_instances = [
            ModelPropertyInstanceDto(
                id=uuid.uuid4(),
                value="0.9",
                model_instance_id=uuid.uuid4(),
                model_property_template_id=template.model_property_templates[0].id,
                model_property_template=template.model_property_templates[0],
            ),
            ModelPropertyInstanceDto(
                id=uuid.uuid4(),
                value="4096",
                model_instance_id=uuid.uuid4(),
                model_property_template_id=template.model_property_templates[1].id,
                model_property_template=template.model_property_templates[1],
            ),
        ]

        instance_dto = ModelInstanceDto(
            id=uuid.uuid4(),
            name="Production GPT-4",
            model_template_id=template.id,
            model_template=template,
            model_property_instances=prop_instances,
        )

        result = mapper.to_target(instance_dto)

        assert result.template_name == "GPT-4 Template"
        assert len(result.properties) == 2

        # Check first property
        assert result.properties[0].key == "temperature"
        assert result.properties[0].value == "0.9"
        assert result.properties[0].label == "Temperature"
        assert result.properties[0].property_type == ModelPropertyType.NUMBER
        assert result.properties[0].required is True

        # Check second property
        assert result.properties[1].key == "max_tokens"
        assert result.properties[1].value == "4096"
        assert result.properties[1].label == "Max Tokens"
        assert result.properties[1].property_type == ModelPropertyType.NUMBER
        assert result.properties[1].required is False

    def test_from_target_not_implemented(self):
        """Test that from_target raises NotImplementedError"""
        mapper = ModelInstanceDtoToModelInstanceToMapper()

        from artemis_model_catalogue_to.model_tos import ModelInstanceTo

        instance_to = ModelInstanceTo(
            id=uuid.uuid4(),
            name="Test",
            model_template_id=uuid.uuid4(),
            template_name="Test Template",
            properties=[],
        )

        with pytest.raises(NotImplementedError):
            mapper.from_target(instance_to)


class TestModelInstanceCreateToToModelInstanceDtoMapper:
    """Test ModelInstanceCreateTo to ModelInstanceDto mapping"""

    def test_basic_mapping(self):
        """Test basic mapping without properties"""
        mapper = ModelInstanceCreateToToModelInstanceDtoMapper()

        create_to = ModelInstanceCreateTo(
            name="New Instance",
            model_template_id=uuid.uuid4(),
        )

        result = mapper.to_target(create_to)

        assert result.id is None
        assert result.name == "New Instance"
        assert result.model_template_id == create_to.model_template_id
        assert result.model_property_instances is None

    def test_with_property_values(self):
        """Test mapping with property values"""
        mapper = ModelInstanceCreateToToModelInstanceDtoMapper()

        template_id = uuid.uuid4()
        create_to = ModelInstanceCreateTo(
            name="New Instance",
            model_template_id=template_id,
            property_values={
                "temperature": "0.8",
                "max_tokens": "2048",
            },
        )

        result = mapper.to_target(create_to)

        # Property instances are not created at mapper level
        # They will be handled by the service layer
        assert result.model_property_instances is None

    def test_from_target_not_implemented(self):
        """Test that from_target raises NotImplementedError"""
        mapper = ModelInstanceCreateToToModelInstanceDtoMapper()

        instance_dto = ModelInstanceDto(
            id=uuid.uuid4(),
            name="Test",
            model_template_id=uuid.uuid4(),
        )

        with pytest.raises(NotImplementedError):
            mapper.from_target(instance_dto)
