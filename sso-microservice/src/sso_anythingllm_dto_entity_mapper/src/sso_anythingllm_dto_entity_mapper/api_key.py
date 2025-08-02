from sso_anythingllm_dto.api_key import ApiKeyDto
from sso_anythingllm_entity.api_key import ApiKey


class ApiKeyDTOEntityMapper:
    """Mapper for ApiKey that includes property templates in the mapping."""

    def from_target(self, target: ApiKey) -> ApiKeyDto:
        """Convert ApiKey entity to DTO."""
        dto = ApiKeyDto(value=target.value)
        return dto

    def to_target(self, source: ApiKeyDto) -> ApiKey:
        """Convert DTO to ApiKey entity."""
        entity = ApiKey(value=source.value)
        return entity
