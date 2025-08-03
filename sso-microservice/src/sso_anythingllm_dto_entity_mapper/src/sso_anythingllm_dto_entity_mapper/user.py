from sso_anythingllm_dto.user import AnythingLLMUserDto
from sso_anythingllm_entity.user import User


class AnythingLLMUserDTOEntityMapper:
    """Mapper for ModelTemplate that includes property templates in the mapping."""

    def from_target(self, target: User) -> AnythingLLMUserDto:
        """Convert ModelTemplate entity to DTO including property templates."""
        dto = AnythingLLMUserDto(
            keycloak_id=target.keycloak_id, name=target.name, internal_id=target.internal_id, role=target.role
        )
        return dto

    def to_target(self, source: AnythingLLMUserDto) -> User:
        dto = User(keycloak_id=source.keycloak_id, name=source.name, internal_id=source.internal_id, role=source.role)
        return dto
