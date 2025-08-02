"""DTO to Entity mapping."""

from pathlib import Path

from sso_anythingllm_dto_entity_mapper.api_key import ApiKeyDTOEntityMapper
from sso_anythingllm_dto_entity_mapper.user import AnythingLLMUserDTOEntityMapper

# Read version from VERSION file
version_file = Path(__file__).parents[2] / "VERSION"
if not version_file.exists():
    raise FileNotFoundError(f"VERSION file not found at {version_file}. Ensure the VERSION file exists in the package")
__version__ = version_file.read_text().strip()


__all__ = ["__version__", "ApiKeyDTOEntityMapper", "AnythingLLMUserDTOEntityMapper"]
