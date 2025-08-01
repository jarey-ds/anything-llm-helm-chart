import uuid

import pytest
from artemis_model_catalogue_dto.model import (
    CapabilityDto,
    ModelInstanceDto,
    ModelPropertyInstanceDto,
    ModelPropertyTemplateDto,
    ModelPropertyTypeDto,
    ModelTemplateCapabilityDto,
    ModelTemplateDto,
    ModelTypeDto,
)
from artemis_model_catalogue_dto_entity_mapper.model import (
    CapabilityDtoEntityMapper,
    ModelInstanceDTOEntityMapper,
    ModelPropertyInstanceDTOEntityMapper,
    ModelPropertyTemplateDTOEntityMapper,
    ModelPropertyTypeDTOEntityMapper,
    ModelTemplateCapabilityDtoEntityMapper,
    ModelTemplateDTOEntityMapper,
    ModelTypeDTOEntityMapper,
)
from artemis_model_catalogue_entity.enums import ModelPropertyType as ModelPropertyTypeEnum
from artemis_model_catalogue_entity.model import (
    Capability,
    ModelInstance,
    ModelPropertyInstance,
    ModelPropertyTemplate,
    ModelPropertyType,
    ModelTemplate,
    ModelTemplateCapability,
    ModelType,
)

# Import provider entities to ensure SQLAlchemy relationships are resolved
from artemis_model_catalogue_entity.provider import ProviderTemplate  # noqa: F401


class TestModelTypeDTOEntityMapper:
    def test_to_target(self):
        mapper = ModelTypeDTOEntityMapper()
        dto = ModelTypeDto(id=uuid.uuid4(), name="chat")

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelType)
        assert entity.id == dto.id
        assert entity.name == dto.name

    def test_from_target(self):
        mapper = ModelTypeDTOEntityMapper()
        entity = ModelType(id=uuid.uuid4(), name="completion")

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelTypeDto)
        assert dto.id == entity.id
        assert dto.name == entity.name

    def test_bidirectional_mapping(self):
        mapper = ModelTypeDTOEntityMapper()
        original_dto = ModelTypeDto(id=uuid.uuid4(), name="embedding")

        entity = mapper.to_target(original_dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.id == original_dto.id
        assert result_dto.name == original_dto.name


class TestModelTemplateDTOEntityMapper:
    def test_to_target(self):
        mapper = ModelTemplateDTOEntityMapper()
        dto = ModelTemplateDto(
            id=uuid.uuid4(),
            name="GPT-4 Template",
            description="Template for GPT-4 models",
            type_id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelTemplate)
        assert entity.id == dto.id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.type_id == dto.type_id
        assert entity.provider_template_id == dto.provider_template_id

    def test_from_target(self):
        mapper = ModelTemplateDTOEntityMapper()
        entity = ModelTemplate(
            id=uuid.uuid4(),
            name="Claude Template",
            description="Template for Claude models",
            type_id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelTemplateDto)
        assert dto.id == entity.id
        assert dto.name == entity.name
        assert dto.description == entity.description
        assert dto.type_id == entity.type_id
        assert dto.provider_template_id == entity.provider_template_id


class TestModelInstanceDTOEntityMapper:
    def test_to_target(self):
        mapper = ModelInstanceDTOEntityMapper()
        dto = ModelInstanceDto(id=uuid.uuid4(), model_template_id=uuid.uuid4(), name="Production GPT-4")

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelInstance)
        assert entity.id == dto.id
        assert entity.model_template_id == dto.model_template_id
        assert entity.name == dto.name

    def test_from_target(self):
        mapper = ModelInstanceDTOEntityMapper()
        entity = ModelInstance(id=uuid.uuid4(), model_template_id=uuid.uuid4(), name="Development Claude")

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelInstanceDto)
        assert dto.id == entity.id
        assert dto.model_template_id == entity.model_template_id
        assert dto.name == entity.name

    def test_with_special_characters_in_name(self):
        mapper = ModelInstanceDTOEntityMapper()
        dto = ModelInstanceDto(id=uuid.uuid4(), model_template_id=uuid.uuid4(), name="Test-Model_v2.0 (beta)")

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.name == dto.name


class TestModelPropertyTypeDTOEntityMapper:
    def test_to_target(self):
        mapper = ModelPropertyTypeDTOEntityMapper()
        dto = ModelPropertyTypeDto(id=uuid.uuid4(), description="Maximum number of tokens", type="integer")

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelPropertyType)
        assert entity.id == dto.id
        assert entity.description == dto.description
        assert entity.type == dto.type

    def test_from_target(self):
        mapper = ModelPropertyTypeDTOEntityMapper()
        entity = ModelPropertyType(id=uuid.uuid4(), name="Temperature", description="Controls randomness", type="float")

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelPropertyTypeDto)
        assert dto.id == entity.id
        assert dto.description == entity.description
        assert dto.type == entity.type

    @pytest.mark.parametrize("type_value", ["string", "boolean", "integer", "float", "array", "object"])
    def test_various_types(self, type_value):
        mapper = ModelPropertyTypeDTOEntityMapper()
        dto = ModelPropertyTypeDto(id=uuid.uuid4(), description=f"Property of type {type_value}", type=type_value)

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.type == type_value


class TestModelPropertyTemplateDTOEntityMapper:
    def test_to_target(self):
        mapper = ModelPropertyTemplateDTOEntityMapper()
        dto = ModelPropertyTemplateDto(
            id=uuid.uuid4(),
            label="Max Tokens",
            key="max_tokens",
            model_template_id=uuid.uuid4(),
            model_property_type_id=uuid.uuid4(),
            required=True,
            default_value="1024",
            property_type=ModelPropertyTypeEnum.NUMBER,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelPropertyTemplate)
        assert entity.id == dto.id
        assert entity.label == dto.label
        assert entity.key == dto.key
        assert entity.model_template_id == dto.model_template_id
        assert entity.model_property_type_id == dto.model_property_type_id
        assert entity.required == dto.required
        assert entity.default_value == dto.default_value

    def test_from_target(self):
        mapper = ModelPropertyTemplateDTOEntityMapper()
        entity = ModelPropertyTemplate(
            id=uuid.uuid4(),
            label="Temperature",
            key="temperature",
            model_template_id=uuid.uuid4(),
            model_property_type_id=uuid.uuid4(),
            required=False,
            default_value="0.7",
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelPropertyTemplateDto)
        assert dto.id == entity.id
        assert dto.label == entity.label
        assert dto.key == entity.key
        assert dto.model_template_id == entity.model_template_id
        assert dto.model_property_type_id == entity.model_property_type_id
        assert dto.required == entity.required
        assert dto.default_value == entity.default_value
        assert dto.property_type == ModelPropertyTypeEnum.TEXT  # Default value when relationship not loaded

    def test_with_none_default_value(self):
        mapper = ModelPropertyTemplateDTOEntityMapper()
        dto = ModelPropertyTemplateDto(
            id=uuid.uuid4(),
            label="Optional Property",
            key="optional_prop",
            model_template_id=uuid.uuid4(),
            model_property_type_id=uuid.uuid4(),
            required=False,
            default_value=None,
            property_type=ModelPropertyTypeEnum.TEXT,
        )

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.default_value is None
        assert result_dto.required is False
        assert result_dto.property_type == ModelPropertyTypeEnum.TEXT  # Default value when relationship not loaded

    def test_from_target_with_relationship_loaded(self):
        mapper = ModelPropertyTemplateDTOEntityMapper()

        # Create entity with relationship loaded
        property_type = ModelPropertyType(id=uuid.uuid4(), description="Number type", type=ModelPropertyTypeEnum.NUMBER)

        entity = ModelPropertyTemplate(
            id=uuid.uuid4(),
            label="Temperature",
            key="temperature",
            model_template_id=uuid.uuid4(),
            model_property_type_id=property_type.id,
            required=False,
            default_value="0.7",
        )
        # Simulate loaded relationship
        entity.model_property_type = property_type

        dto = mapper.from_target(entity)

        assert dto.property_type == ModelPropertyTypeEnum.NUMBER  # Should use the actual type from relationship


class TestModelPropertyInstanceDTOEntityMapper:
    def test_to_target(self):
        mapper = ModelPropertyInstanceDTOEntityMapper()
        dto = ModelPropertyInstanceDto(
            id=uuid.uuid4(), value="2048", model_instance_id=uuid.uuid4(), model_property_template_id=uuid.uuid4()
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelPropertyInstance)
        assert entity.id == dto.id
        assert entity.value == dto.value
        assert entity.model_instance_id == dto.model_instance_id
        assert entity.model_property_template_id == dto.model_property_template_id

    def test_from_target(self):
        mapper = ModelPropertyInstanceDTOEntityMapper()
        entity = ModelPropertyInstance(
            id=uuid.uuid4(), value="0.9", model_instance_id=uuid.uuid4(), model_property_template_id=uuid.uuid4()
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelPropertyInstanceDto)
        assert dto.id == entity.id
        assert dto.value == entity.value
        assert dto.model_instance_id == entity.model_instance_id
        assert dto.model_property_template_id == entity.model_property_template_id

    def test_with_json_value(self):
        mapper = ModelPropertyInstanceDTOEntityMapper()
        json_value = '{"key": "value", "nested": {"array": [1, 2, 3]}}'
        dto = ModelPropertyInstanceDto(
            id=uuid.uuid4(), value=json_value, model_instance_id=uuid.uuid4(), model_property_template_id=uuid.uuid4()
        )

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.value == json_value


class TestCapabilityDtoEntityMapper:
    def test_to_target(self):
        mapper = CapabilityDtoEntityMapper()
        dto = CapabilityDto(
            id=uuid.uuid4(), name="function_calling", description="Supports function calling capabilities", value="true"
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, Capability)
        assert entity.id == dto.id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.value == dto.value

    def test_from_target(self):
        mapper = CapabilityDtoEntityMapper()
        entity = Capability(
            id=uuid.uuid4(), name="streaming", description="Supports streaming responses", value="false"
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, CapabilityDto)
        assert dto.id == entity.id
        assert dto.name == entity.name
        assert dto.description == entity.description
        assert dto.value == entity.value

    def test_with_complex_value(self):
        mapper = CapabilityDtoEntityMapper()
        dto = CapabilityDto(
            id=uuid.uuid4(),
            name="supported_formats",
            description="List of supported formats",
            value='["json", "xml", "yaml"]',
        )

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.value == dto.value


class TestModelTemplateCapabilityDtoEntityMapper:
    def test_to_target(self):
        mapper = ModelTemplateCapabilityDtoEntityMapper()
        dto = ModelTemplateCapabilityDto(
            id=uuid.uuid4(), model_template_id=uuid.uuid4(), model_capability_id=uuid.uuid4()
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ModelTemplateCapability)
        assert entity.id == dto.id
        assert entity.model_template_id == dto.model_template_id
        assert entity.model_capability_id == dto.model_capability_id

    def test_from_target(self):
        mapper = ModelTemplateCapabilityDtoEntityMapper()
        entity = ModelTemplateCapability(
            id=uuid.uuid4(), model_template_id=uuid.uuid4(), model_capability_id=uuid.uuid4()
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ModelTemplateCapabilityDto)
        assert dto.id == entity.id
        assert dto.model_template_id == entity.model_template_id
        assert dto.model_capability_id == entity.model_capability_id

    def test_bidirectional_mapping(self):
        mapper = ModelTemplateCapabilityDtoEntityMapper()
        original_dto = ModelTemplateCapabilityDto(
            id=uuid.uuid4(), model_template_id=uuid.uuid4(), model_capability_id=uuid.uuid4()
        )

        entity = mapper.to_target(original_dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.id == original_dto.id
        assert result_dto.model_template_id == original_dto.model_template_id
        assert result_dto.model_capability_id == original_dto.model_capability_id
