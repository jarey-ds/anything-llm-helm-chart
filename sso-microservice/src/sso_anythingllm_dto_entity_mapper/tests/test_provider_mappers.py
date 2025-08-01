import uuid

import pytest
from artemis_model_catalogue_dto.provider import (
    OwnerTypeDto,
    ProviderInstanceCreateDto,
    ProviderInstanceDto,
    ProviderModelDto,
    ProviderPropertyInstanceDto,
    ProviderPropertyTemplateCreateDto,
    ProviderPropertyTemplateDto,
    ProviderPropertyTypeCreateDto,
    ProviderPropertyTypeDto,
    ProviderTemplateDto,
)
from artemis_model_catalogue_dto_entity_mapper.provider import (
    OwnerTypeDTOEntityMapper,
    ProviderInstanceCreateDTOEntityMapper,
    ProviderInstanceCreateWithPropertiesDTOEntityMapper,
    ProviderInstanceDTOEntityMapper,
    ProviderInstanceWithPropertiesDTOEntityMapper,
    ProviderModelDTOEntityMapper,
    ProviderPropertyInstanceDTOEntityMapper,
    ProviderPropertyTemplateCreateDTOEntityMapper,
    ProviderPropertyTemplateDTOEntityMapper,
    ProviderPropertyTypeCreateDTOEntityMapper,
    ProviderPropertyTypeDTOEntityMapper,
    ProviderTemplateDTOEntityMapper,
    ProviderTemplateWithPropertiesDTOEntityMapper,
)
from artemis_model_catalogue_entity.provider import (
    OwnerType,
    ProviderInstance,
    ProviderModel,
    ProviderPropertyInstance,
    ProviderPropertyTemplate,
    ProviderPropertyType,
    ProviderTemplate,
)
from artemis_model_catalogue_service.common_models import PropertyType


class TestOwnerTypeDTOEntityMapper:
    def test_to_target(self):
        mapper = OwnerTypeDTOEntityMapper()
        dto = OwnerTypeDto(id=uuid.uuid4(), name="user")

        entity = mapper.to_target(dto)

        assert isinstance(entity, OwnerType)
        assert entity.id == dto.id
        assert entity.name == dto.name

    def test_from_target(self):
        mapper = OwnerTypeDTOEntityMapper()
        entity = OwnerType(id=uuid.uuid4(), name="organization")

        dto = mapper.from_target(entity)

        assert isinstance(dto, OwnerTypeDto)
        assert dto.id == entity.id
        assert dto.name == entity.name

    @pytest.mark.parametrize("owner_type", ["user", "team", "organization"])
    def test_various_owner_types(self, owner_type):
        mapper = OwnerTypeDTOEntityMapper()
        dto = OwnerTypeDto(id=uuid.uuid4(), name=owner_type)

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.name == owner_type


class TestProviderTemplateDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderTemplateDTOEntityMapper()
        dto = ProviderTemplateDto(
            id=uuid.uuid4(),
            name="OpenAI Provider",
            description="Provider template for OpenAI services",
            overridable=True,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderTemplate)
        assert entity.id == dto.id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.overridable == dto.overridable

    def test_from_target(self):
        mapper = ProviderTemplateDTOEntityMapper()
        entity = ProviderTemplate(
            id=uuid.uuid4(),
            name="Anthropic Provider",
            description="Provider template for Anthropic services",
            overridable=False,
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderTemplateDto)
        assert dto.id == entity.id
        assert dto.name == entity.name
        assert dto.description == entity.description
        assert dto.overridable == entity.overridable

    @pytest.mark.parametrize("overridable", [True, False])
    def test_overridable_flag(self, overridable):
        mapper = ProviderTemplateDTOEntityMapper()
        dto = ProviderTemplateDto(
            id=uuid.uuid4(), name=f"Provider {overridable}", description="Test provider", overridable=overridable
        )

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.overridable == overridable

    def test_from_target_with_embedded_property_templates(self):
        """Test that from_target properly maps embedded property templates."""
        # Use the mapper that handles properties
        mapper = ProviderTemplateWithPropertiesDTOEntityMapper()

        # Create entity with property templates
        template_id = uuid.uuid4()
        entity = ProviderTemplate(
            id=template_id,
            name="Test Provider",
            description="Provider with embedded properties",
            overridable=True,
        )

        # Add property templates to the entity
        prop_template_1 = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="API Key",
            key="api_key",
            provider_template_id=template_id,
            property_type=PropertyType.PASSWORD.value,
            required=True,
            default_value=None,
        )
        prop_template_2 = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="Base URL",
            key="base_url",
            provider_template_id=template_id,
            property_type=PropertyType.URL.value,
            required=True,
            default_value="https://api.example.com",
        )
        entity.property_templates = [prop_template_1, prop_template_2]

        # Convert to DTO
        dto = mapper.from_target(entity)

        # Assert that property templates were mapped
        assert dto.property_templates is not None
        assert len(dto.property_templates) == 2
        assert dto.property_templates[0].key == "api_key"
        assert dto.property_templates[0].property_type == PropertyType.PASSWORD.value
        assert dto.property_templates[1].key == "base_url"
        assert dto.property_templates[1].property_type == PropertyType.URL.value
        assert dto.property_templates[1].default_value == "https://api.example.com"

    def test_from_target_without_properties_returns_none(self):
        """Test that basic mapper always returns None for property_templates."""
        mapper = ProviderTemplateDTOEntityMapper()

        # Create entity with property templates
        template_id = uuid.uuid4()
        entity = ProviderTemplate(
            id=template_id,
            name="Test Provider",
            description="Provider with embedded properties",
            overridable=True,
        )

        # Add property templates to the entity (they should be ignored)
        prop_template_1 = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="API Key",
            key="api_key",
            provider_template_id=template_id,
            property_type=PropertyType.PASSWORD.value,
            required=True,
            default_value=None,
        )
        entity.property_templates = [prop_template_1]

        # Convert to DTO
        dto = mapper.from_target(entity)

        # Assert that property templates is None
        assert dto.property_templates is None


class TestProviderInstanceDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderInstanceDTOEntityMapper()
        dto = ProviderInstanceDto(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Production OpenAI Instance",
            description="Production OpenAI provider instance",
            overridable=True,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderInstance)
        assert entity.id == dto.id
        assert entity.provider_template_id == dto.provider_template_id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.overridable == dto.overridable

    def test_from_target(self):
        mapper = ProviderInstanceDTOEntityMapper()
        entity = ProviderInstance(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Development Anthropic Instance",
            description="Development Anthropic provider instance",
            overridable=True,
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderInstanceDto)
        assert dto.id == entity.id
        assert dto.provider_template_id == entity.provider_template_id
        assert dto.name == entity.name
        assert dto.description == entity.description
        assert dto.overridable == entity.overridable

    def test_with_special_characters_in_name(self):
        mapper = ProviderInstanceDTOEntityMapper()
        dto = ProviderInstanceDto(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Test-Provider_v1.0 (staging)",
            description="Test provider with special chars",
            overridable=True,
        )

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.name == dto.name
        assert result_dto.description == dto.description
        assert result_dto.overridable == dto.overridable


class TestProviderPropertyTypeDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderPropertyTypeDTOEntityMapper()
        dto = ProviderPropertyTypeDto(description="API Key property", type="string")

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderPropertyType)
        assert entity.id == dto.type  # id is mapped from type
        assert entity.description == dto.description
        assert entity.type == dto.type

    def test_from_target(self):
        mapper = ProviderPropertyTypeDTOEntityMapper()
        entity = ProviderPropertyType(id="url", description="Endpoint URL property")

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderPropertyTypeDto)
        assert dto.type == entity.id  # type is mapped from id
        assert dto.description == entity.description

    @pytest.mark.parametrize("prop_type", ["string", "integer", "boolean", "url", "secret", "json"])
    def test_various_property_types(self, prop_type):
        mapper = ProviderPropertyTypeDTOEntityMapper()
        dto = ProviderPropertyTypeDto(description=f"Property of type {prop_type}", type=prop_type)

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.type == prop_type


class TestProviderPropertyTypeCreateDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderPropertyTypeCreateDTOEntityMapper()
        dto = ProviderPropertyTypeCreateDto(description="SSH Key property type", type="ssh_key")

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderPropertyType)
        assert entity.id == dto.type  # type is mapped to id
        assert entity.description == dto.description
        assert entity.type == dto.type

    def test_from_target(self):
        mapper = ProviderPropertyTypeCreateDTOEntityMapper()
        entity = ProviderPropertyType(id="certificate", description="Certificate property type")

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderPropertyTypeCreateDto)
        assert dto.type == entity.id  # id is mapped to type
        assert dto.description == entity.description

    def test_bidirectional_mapping(self):
        mapper = ProviderPropertyTypeCreateDTOEntityMapper()
        original_dto = ProviderPropertyTypeCreateDto(description="API token property", type="api_token")

        entity = mapper.to_target(original_dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.type == original_dto.type
        assert result_dto.description == original_dto.description

    @pytest.mark.parametrize("prop_type", ["text", "password", "url", "email", "number", "json", "file"])
    def test_various_property_types(self, prop_type):
        mapper = ProviderPropertyTypeCreateDTOEntityMapper()
        dto = ProviderPropertyTypeCreateDto(description=f"Property of type {prop_type}", type=prop_type)

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.type == prop_type
        assert result_dto.description == f"Property of type {prop_type}"


class TestProviderPropertyTemplateDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderPropertyTemplateDTOEntityMapper()
        dto = ProviderPropertyTemplateDto(
            id=uuid.uuid4(),
            label="API Key",
            key="api_key",
            provider_template_id=uuid.uuid4(),
            property_type=PropertyType.PASSWORD.value,
            required=True,
            default_value=None,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderPropertyTemplate)
        assert entity.id == dto.id
        assert entity.label == dto.label
        assert entity.key == dto.key
        assert entity.provider_template_id == dto.provider_template_id
        assert entity.property_type == dto.property_type
        assert entity.required == dto.required
        assert entity.default_value == dto.default_value

    def test_from_target(self):
        mapper = ProviderPropertyTemplateDTOEntityMapper()
        entity = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="Base URL",
            key="base_url",
            provider_template_id=uuid.uuid4(),
            property_type=PropertyType.URL.value,
            required=False,
            default_value="https://api.openai.com",
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderPropertyTemplateDto)
        assert dto.id == entity.id
        assert dto.label == entity.label
        assert dto.key == entity.key
        assert dto.provider_template_id == entity.provider_template_id
        assert dto.property_type == entity.property_type
        assert dto.required == entity.required
        assert dto.default_value == entity.default_value

    def test_with_default_value(self):
        mapper = ProviderPropertyTemplateDTOEntityMapper()
        dto = ProviderPropertyTemplateDto(
            id=uuid.uuid4(),
            label="Timeout",
            key="timeout",
            provider_template_id=uuid.uuid4(),
            property_type=PropertyType.NUMBER.value,
            required=False,
            default_value="30",
        )

        entity = mapper.to_target(dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.default_value == "30"
        assert result_dto.required is False


class TestProviderPropertyInstanceDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderPropertyInstanceDTOEntityMapper()
        dto = ProviderPropertyInstanceDto(
            id=uuid.uuid4(),
            key="api_key",
            value="sk-1234567890abcdef",
            provider_instance_id=uuid.uuid4(),
            property_template_id=uuid.uuid4(),
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderPropertyInstance)
        assert entity.id == dto.id
        assert entity.value == dto.value
        assert entity.provider_instance_id == dto.provider_instance_id
        assert entity.property_template_id == dto.property_template_id

    def test_from_target(self):
        mapper = ProviderPropertyInstanceDTOEntityMapper()

        # Create a mock property template with the key
        mock_property_template = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="API Key",
            key="api_key",
            provider_template_id=uuid.uuid4(),
            property_type="text",
            required=True,
        )

        entity = ProviderPropertyInstance(
            id=uuid.uuid4(),
            value="https://api.anthropic.com/v1",
            provider_instance_id=uuid.uuid4(),
            property_template_id=mock_property_template.id,
        )
        # Set the property_template relationship
        entity.property_template = mock_property_template

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderPropertyInstanceDto)
        assert dto.id == entity.id
        assert dto.value == entity.value
        assert dto.provider_instance_id == entity.provider_instance_id
        assert dto.property_template_id == entity.property_template_id
        assert dto.key == "api_key"

    def test_with_json_value(self):
        mapper = ProviderPropertyInstanceDTOEntityMapper()
        json_value = '{"region": "us-east-1", "version": "2023-01-01"}'

        # Create a mock property template
        mock_property_template = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="Config",
            key="config",
            provider_template_id=uuid.uuid4(),
            property_type="json",
            required=True,
        )

        dto = ProviderPropertyInstanceDto(
            id=uuid.uuid4(),
            key="config",
            value=json_value,
            provider_instance_id=uuid.uuid4(),
            property_template_id=mock_property_template.id,
        )

        entity = mapper.to_target(dto)
        # Set the property_template relationship
        entity.property_template = mock_property_template

        result_dto = mapper.from_target(entity)

        assert result_dto.value == json_value
        assert result_dto.key == "config"

    def test_with_empty_value(self):
        mapper = ProviderPropertyInstanceDTOEntityMapper()

        # Create a mock property template
        mock_property_template = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="Empty Field",
            key="empty_field",
            provider_template_id=uuid.uuid4(),
            property_type="text",
            required=False,
        )

        dto = ProviderPropertyInstanceDto(
            id=uuid.uuid4(),
            key="empty_field",
            value="",
            provider_instance_id=uuid.uuid4(),
            property_template_id=mock_property_template.id,
        )

        entity = mapper.to_target(dto)
        # Set the property_template relationship
        entity.property_template = mock_property_template

        result_dto = mapper.from_target(entity)

        assert result_dto.value == ""
        assert result_dto.key == "empty_field"


class TestProviderModelDTOEntityMapper:
    def test_to_target(self):
        mapper = ProviderModelDTOEntityMapper()
        dto = ProviderModelDto(
            id=uuid.uuid4(),
            model_instance_id=uuid.uuid4(),
            provider_instance_id=uuid.uuid4(),
            owner_id=uuid.uuid4(),
            owner_type_id=uuid.uuid4(),
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderModel)
        assert entity.id == dto.id
        assert entity.model_instance_id == dto.model_instance_id
        assert entity.provider_instance_id == dto.provider_instance_id
        assert entity.owner_id == dto.owner_id
        assert entity.owner_type_id == dto.owner_type_id

    def test_from_target(self):
        mapper = ProviderModelDTOEntityMapper()
        entity = ProviderModel(
            id=uuid.uuid4(),
            model_instance_id=uuid.uuid4(),
            provider_instance_id=uuid.uuid4(),
            owner_id=uuid.uuid4(),
            owner_type_id=uuid.uuid4(),
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderModelDto)
        assert dto.id == entity.id
        assert dto.model_instance_id == entity.model_instance_id
        assert dto.provider_instance_id == entity.provider_instance_id
        assert dto.owner_id == entity.owner_id
        assert dto.owner_type_id == entity.owner_type_id

    def test_bidirectional_mapping(self):
        mapper = ProviderModelDTOEntityMapper()
        original_dto = ProviderModelDto(
            id=uuid.uuid4(),
            model_instance_id=uuid.uuid4(),
            provider_instance_id=uuid.uuid4(),
            owner_id=uuid.uuid4(),
            owner_type_id=uuid.uuid4(),
        )

        entity = mapper.to_target(original_dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.id == original_dto.id
        assert result_dto.model_instance_id == original_dto.model_instance_id
        assert result_dto.provider_instance_id == original_dto.provider_instance_id
        assert result_dto.owner_id == original_dto.owner_id
        assert result_dto.owner_type_id == original_dto.owner_type_id


class TestProviderTemplateCreateDTOEntityMapper:
    """Test for ProviderTemplateCreateDTOEntityMapper with embedded property templates."""

    def test_to_target_without_properties(self):
        """Test mapping without property templates."""
        from artemis_model_catalogue_dto.provider import ProviderTemplateCreateDto
        from artemis_model_catalogue_dto_entity_mapper.provider import ProviderTemplateCreateDTOEntityMapper

        mapper = ProviderTemplateCreateDTOEntityMapper()
        dto = ProviderTemplateCreateDto(
            name="Simple Provider",
            description="A simple provider without properties",
            overridable=True,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderTemplate)
        assert entity.name == "Simple Provider"
        assert entity.description == "A simple provider without properties"
        assert entity.overridable is True
        assert entity.property_templates == []

    def test_to_target_with_embedded_properties(self):
        """Test mapping with embedded property templates."""
        from artemis_model_catalogue_dto.provider import ProviderPropertyTemplateCreateDto, ProviderTemplateCreateDto
        from artemis_model_catalogue_dto_entity_mapper.provider import ProviderTemplateCreateDTOEntityMapper

        mapper = ProviderTemplateCreateDTOEntityMapper()

        # Create DTO with embedded property templates
        dto = ProviderTemplateCreateDto(
            name="Complex Provider",
            description="A provider with embedded properties",
            overridable=False,
            property_templates=[
                ProviderPropertyTemplateCreateDto(
                    label="API Key",
                    key="api_key",
                    property_type=PropertyType.PASSWORD.value,
                    required=True,
                    default_value=None,
                ),
                ProviderPropertyTemplateCreateDto(
                    label="Endpoint URL",
                    key="endpoint_url",
                    property_type=PropertyType.URL.value,
                    required=True,
                    default_value="https://api.default.com",
                ),
                ProviderPropertyTemplateCreateDto(
                    label="Timeout",
                    key="timeout",
                    property_type=PropertyType.NUMBER.value,
                    required=False,
                    default_value="30",
                ),
            ],
        )

        entity = mapper.to_target(dto)

        # Check main entity properties
        assert isinstance(entity, ProviderTemplate)
        assert entity.name == "Complex Provider"
        assert entity.description == "A provider with embedded properties"
        assert entity.overridable is False

        # Check embedded property templates
        assert len(entity.property_templates) == 3

        # Check first property
        assert entity.property_templates[0].label == "API Key"
        assert entity.property_templates[0].key == "api_key"
        assert entity.property_templates[0].property_type == PropertyType.PASSWORD.value
        assert entity.property_templates[0].required is True
        assert entity.property_templates[0].default_value is None
        assert entity.property_templates[0].provider_template_id == entity.id

        # Check second property
        assert entity.property_templates[1].label == "Endpoint URL"
        assert entity.property_templates[1].key == "endpoint_url"
        assert entity.property_templates[1].property_type == PropertyType.URL.value
        assert entity.property_templates[1].required is True
        assert entity.property_templates[1].default_value == "https://api.default.com"
        assert entity.property_templates[1].provider_template_id == entity.id

        # Check third property
        assert entity.property_templates[2].label == "Timeout"
        assert entity.property_templates[2].key == "timeout"
        assert entity.property_templates[2].property_type == PropertyType.NUMBER.value
        assert entity.property_templates[2].required is False
        assert entity.property_templates[2].default_value == "30"
        assert entity.property_templates[2].provider_template_id == entity.id


class TestProviderInstanceCreateDTOEntityMapper:
    """Test for ProviderInstanceCreateDTOEntityMapper."""

    def test_to_target(self):
        """Test mapping ProviderInstanceCreateDto to ProviderInstance entity."""
        mapper = ProviderInstanceCreateDTOEntityMapper()
        dto = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Test Provider Instance",
            description="A test provider instance",
            overridable=True,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderInstance)
        assert entity.id is not None  # ID should be auto-generated
        assert entity.provider_template_id == dto.provider_template_id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.overridable == dto.overridable

    def test_to_target_with_different_overridable_values(self):
        """Test mapping with different overridable values."""
        mapper = ProviderInstanceCreateDTOEntityMapper()

        # Test with overridable=False
        dto_false = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Non-overridable Instance",
            description="This instance cannot be overridden",
            overridable=False,
        )
        entity_false = mapper.to_target(dto_false)
        assert entity_false.overridable is False

        # Test with overridable=True
        dto_true = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Overridable Instance",
            description="This instance can be overridden",
            overridable=True,
        )
        entity_true = mapper.to_target(dto_true)
        assert entity_true.overridable is True

    def test_from_target_not_implemented(self):
        """Test that from_target raises NotImplementedError."""
        mapper = ProviderInstanceCreateDTOEntityMapper()
        entity = ProviderInstance(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Test Instance",
            description="Test description",
            overridable=True,
        )

        with pytest.raises(NotImplementedError):
            mapper.from_target(entity)


class TestProviderPropertyTemplateCreateDTOEntityMapper:
    """Test for standalone ProviderPropertyTemplateCreateDTOEntityMapper."""

    def test_to_target_without_provider_template_id(self):
        """Test mapping without provider_template_id."""
        mapper = ProviderPropertyTemplateCreateDTOEntityMapper()
        dto = ProviderPropertyTemplateCreateDto(
            label="API Key",
            key="api_key",
            property_type=PropertyType.PASSWORD.value,
            required=True,
            default_value=None,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderPropertyTemplate)
        assert entity.id is not None  # ID should be auto-generated
        assert entity.label == "API Key"
        assert entity.key == "api_key"
        assert entity.property_type == PropertyType.PASSWORD.value
        assert entity.required is True
        assert entity.default_value is None
        assert entity.provider_template_id is None  # No provider_template_id set

    def test_to_target_with_provider_template_id(self):
        """Test mapping with provider_template_id."""
        provider_template_id = uuid.uuid4()
        mapper = ProviderPropertyTemplateCreateDTOEntityMapper(provider_template_id)
        dto = ProviderPropertyTemplateCreateDto(
            label="Base URL",
            key="base_url",
            property_type=PropertyType.URL.value,
            required=True,
            default_value="https://api.example.com",
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderPropertyTemplate)
        assert entity.provider_template_id == provider_template_id
        assert entity.label == "Base URL"
        assert entity.key == "base_url"
        assert entity.property_type == PropertyType.URL.value
        assert entity.required is True
        assert entity.default_value == "https://api.example.com"

    def test_to_target_with_optional_property(self):
        """Test mapping with optional property and default value."""
        mapper = ProviderPropertyTemplateCreateDTOEntityMapper()
        dto = ProviderPropertyTemplateCreateDto(
            label="Timeout",
            key="timeout",
            property_type=PropertyType.NUMBER.value,
            required=False,
            default_value="30",
        )

        entity = mapper.to_target(dto)

        assert entity.label == "Timeout"
        assert entity.key == "timeout"
        assert entity.property_type == PropertyType.NUMBER.value
        assert entity.required is False
        assert entity.default_value == "30"

    @pytest.mark.parametrize(
        "prop_type,label,key",
        [
            ("text", "Description", "description"),
            ("password", "Secret Key", "secret_key"),
            ("url", "Webhook URL", "webhook_url"),
            ("email", "Contact Email", "contact_email"),
            ("number", "Max Retries", "max_retries"),
            ("boolean", "Enable Debug", "enable_debug"),
            ("json", "Configuration", "config"),
        ],
    )
    def test_various_property_types(self, prop_type, label, key):
        """Test mapping with various property types."""
        mapper = ProviderPropertyTemplateCreateDTOEntityMapper()
        dto = ProviderPropertyTemplateCreateDto(
            label=label,
            key=key,
            property_type=prop_type,
            required=True,
            default_value=None,
        )

        entity = mapper.to_target(dto)

        assert entity.label == label
        assert entity.key == key
        assert entity.property_type == prop_type
        assert entity.required is True

    def test_from_target_not_implemented(self):
        """Test that from_target raises NotImplementedError."""
        mapper = ProviderPropertyTemplateCreateDTOEntityMapper()
        entity = ProviderPropertyTemplate(
            id=uuid.uuid4(),
            label="Test",
            key="test",
            provider_template_id=uuid.uuid4(),
            property_type=PropertyType.TEXT.value,
            required=True,
            default_value=None,
        )

        with pytest.raises(NotImplementedError):
            mapper.from_target(entity)


class TestProviderInstanceCreateWithPropertiesDTOEntityMapper:
    """Test for ProviderInstanceCreateWithPropertiesDTOEntityMapper."""

    def test_to_target_without_property_values(self):
        """Test mapping without property values."""
        # Create property templates
        property_templates = [
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="API Key",
                key="api_key",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.PASSWORD.value,
                required=True,
                default_value=None,
            ),
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="Base URL",
                key="base_url",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.URL.value,
                required=False,
                default_value="https://api.default.com",
            ),
        ]

        mapper = ProviderInstanceCreateWithPropertiesDTOEntityMapper(property_templates)
        dto = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Test Provider Instance",
            description="Instance without property values",
            overridable=True,
            property_values=None,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderInstance)
        assert entity.provider_template_id == dto.provider_template_id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.overridable == dto.overridable
        assert len(entity.property_instances) == 0  # No property instances created

    def test_to_target_with_property_values(self):
        """Test mapping with property values."""
        # Create property templates
        template_1_id = uuid.uuid4()
        template_2_id = uuid.uuid4()
        property_templates = [
            ProviderPropertyTemplate(
                id=template_1_id,
                label="API Key",
                key="api_key",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.PASSWORD.value,
                required=True,
                default_value=None,
            ),
            ProviderPropertyTemplate(
                id=template_2_id,
                label="Base URL",
                key="base_url",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.URL.value,
                required=True,
                default_value=None,
            ),
        ]

        mapper = ProviderInstanceCreateWithPropertiesDTOEntityMapper(property_templates)
        dto = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Test Provider Instance",
            description="Instance with property values",
            overridable=False,
            property_values={
                "api_key": "sk-1234567890",
                "base_url": "https://api.example.com",
            },
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderInstance)
        assert len(entity.property_instances) == 2

        # Check property instances
        property_map = {pi.property_template_id: pi for pi in entity.property_instances}

        # Check API Key property instance
        api_key_instance = property_map[template_1_id]
        assert api_key_instance.value == "sk-1234567890"
        assert api_key_instance.provider_instance_id == entity.id

        # Check Base URL property instance
        base_url_instance = property_map[template_2_id]
        assert base_url_instance.value == "https://api.example.com"
        assert base_url_instance.provider_instance_id == entity.id

    def test_to_target_with_default_values(self):
        """Test mapping with default values for non-required properties."""
        # Create property templates with defaults
        property_templates = [
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="API Key",
                key="api_key",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.PASSWORD.value,
                required=True,
                default_value=None,
            ),
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="Timeout",
                key="timeout",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.NUMBER.value,
                required=False,
                default_value="30",
            ),
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="Retry Count",
                key="retry_count",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.NUMBER.value,
                required=False,
                default_value="3",
            ),
        ]

        mapper = ProviderInstanceCreateWithPropertiesDTOEntityMapper(property_templates)
        dto = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Test Provider Instance",
            description="Instance with default values",
            overridable=True,
            property_values={
                "api_key": "sk-test-key",
                # timeout not provided, should use default
                # retry_count not provided, should use default
            },
        )

        entity = mapper.to_target(dto)

        assert len(entity.property_instances) == 3  # All properties should have instances

        # Check that defaults were applied
        property_map = {pi.property_template_id: pi.value for pi in entity.property_instances}

        # Find the property instances by matching template IDs
        timeout_template = next(t for t in property_templates if t.key == "timeout")
        retry_template = next(t for t in property_templates if t.key == "retry_count")

        assert property_map[timeout_template.id] == "30"
        assert property_map[retry_template.id] == "3"

    def test_to_target_with_mixed_property_values(self):
        """Test mapping with some properties provided and some using defaults."""
        property_templates = [
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="API Key",
                key="api_key",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.PASSWORD.value,
                required=True,
                default_value=None,
            ),
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="Region",
                key="region",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.TEXT.value,
                required=False,
                default_value="us-east-1",
            ),
            ProviderPropertyTemplate(
                id=uuid.uuid4(),
                label="Environment",
                key="environment",
                provider_template_id=uuid.uuid4(),
                property_type=PropertyType.TEXT.value,
                required=False,
                default_value="production",
            ),
        ]

        mapper = ProviderInstanceCreateWithPropertiesDTOEntityMapper(property_templates)
        dto = ProviderInstanceCreateDto(
            provider_template_id=uuid.uuid4(),
            name="Mixed Properties Instance",
            description="Instance with mixed property values",
            overridable=True,
            property_values={
                "api_key": "sk-mixed-test",
                "region": "eu-west-1",  # Override default
                # environment not provided, should use default "production"
            },
        )

        entity = mapper.to_target(dto)

        assert len(entity.property_instances) == 3

        # Verify values
        value_map = {}
        for pi in entity.property_instances:
            for template in property_templates:
                if pi.property_template_id == template.id:
                    value_map[template.key] = pi.value
                    break

        assert value_map["api_key"] == "sk-mixed-test"
        assert value_map["region"] == "eu-west-1"  # Overridden value
        assert value_map["environment"] == "production"  # Default value

    def test_from_target_not_implemented(self):
        """Test that from_target raises NotImplementedError."""
        property_templates = []
        mapper = ProviderInstanceCreateWithPropertiesDTOEntityMapper(property_templates)
        entity = ProviderInstance(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Test Instance",
            description="Test description",
            overridable=True,
        )

        with pytest.raises(NotImplementedError):
            mapper.from_target(entity)


class TestProviderInstanceWithPropertiesDTOEntityMapper:
    """Test for ProviderInstanceWithPropertiesDTOEntityMapper."""

    def test_to_target(self):
        """Test mapping ProviderInstanceDto to ProviderInstance entity."""
        mapper = ProviderInstanceWithPropertiesDTOEntityMapper()
        dto = ProviderInstanceDto(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Test Provider Instance",
            description="A test provider instance",
            overridable=True,
            property_instances=None,
        )

        entity = mapper.to_target(dto)

        assert isinstance(entity, ProviderInstance)
        assert entity.id == dto.id
        assert entity.provider_template_id == dto.provider_template_id
        assert entity.name == dto.name
        assert entity.description == dto.description
        assert entity.overridable == dto.overridable

    def test_from_target_without_properties(self):
        """Test mapping from entity without property instances."""
        mapper = ProviderInstanceWithPropertiesDTOEntityMapper()
        entity = ProviderInstance(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Test Provider",
            description="Provider without properties",
            overridable=True,
        )

        dto = mapper.from_target(entity)

        assert isinstance(dto, ProviderInstanceDto)
        assert dto.id == entity.id
        assert dto.provider_template_id == entity.provider_template_id
        assert dto.name == entity.name
        assert dto.description == entity.description
        assert dto.overridable == entity.overridable
        assert dto.property_instances == []

    def test_from_target_with_properties(self):
        """Test mapping from entity with property instances."""
        mapper = ProviderInstanceWithPropertiesDTOEntityMapper()

        # Create entity with property instances
        instance_id = uuid.uuid4()
        entity = ProviderInstance(
            id=instance_id,
            provider_template_id=uuid.uuid4(),
            name="Test Provider",
            description="Provider with properties",
            overridable=False,
        )

        # Add property instances
        prop_instance_1 = ProviderPropertyInstance(
            id=uuid.uuid4(),
            value="sk-1234567890",
            provider_instance_id=instance_id,
            property_template_id=uuid.uuid4(),
        )
        prop_instance_2 = ProviderPropertyInstance(
            id=uuid.uuid4(),
            value="https://api.example.com",
            provider_instance_id=instance_id,
            property_template_id=uuid.uuid4(),
        )

        # Add property templates to property instances for key mapping
        prop_instance_1.property_template = ProviderPropertyTemplate(
            id=prop_instance_1.property_template_id,
            label="API Key",
            key="api_key",
            provider_template_id=uuid.uuid4(),
            property_type=PropertyType.PASSWORD.value,
            required=True,
            default_value=None,
        )
        prop_instance_2.property_template = ProviderPropertyTemplate(
            id=prop_instance_2.property_template_id,
            label="Base URL",
            key="base_url",
            provider_template_id=uuid.uuid4(),
            property_type=PropertyType.URL.value,
            required=True,
            default_value=None,
        )

        entity.property_instances = [prop_instance_1, prop_instance_2]

        dto = mapper.from_target(entity)

        assert dto.property_instances is not None
        assert len(dto.property_instances) == 2

        # Check first property instance
        assert dto.property_instances[0].value == "sk-1234567890"
        assert dto.property_instances[0].key == "api_key"

        # Check second property instance
        assert dto.property_instances[1].value == "https://api.example.com"
        assert dto.property_instances[1].key == "base_url"

    def test_bidirectional_mapping(self):
        """Test mapping back and forth."""
        mapper = ProviderInstanceWithPropertiesDTOEntityMapper()
        original_dto = ProviderInstanceDto(
            id=uuid.uuid4(),
            provider_template_id=uuid.uuid4(),
            name="Bidirectional Test",
            description="Testing bidirectional mapping",
            overridable=True,
            property_instances=None,
        )

        entity = mapper.to_target(original_dto)
        result_dto = mapper.from_target(entity)

        assert result_dto.id == original_dto.id
        assert result_dto.provider_template_id == original_dto.provider_template_id
        assert result_dto.name == original_dto.name
        assert result_dto.description == original_dto.description
        assert result_dto.overridable == original_dto.overridable
