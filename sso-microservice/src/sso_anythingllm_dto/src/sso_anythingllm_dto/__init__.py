"""Data Transfer Objects."""

from pathlib import Path

from sso_anythingllm_dto.api_key import ApiKeyDto
from sso_anythingllm_dto.user import AnythingLLMUserDto, KeycloakUserDto

# Read version from VERSION file
version_file = Path(__file__).parents[2] / "VERSION"
if not version_file.exists():
    raise FileNotFoundError(f"VERSION file not found at {version_file}. Ensure the VERSION file exists in the package")
__version__ = version_file.read_text().strip()


__all__ = ["__version__", "ApiKeyDto", "AnythingLLMUserDto", "KeycloakUserDto"]
