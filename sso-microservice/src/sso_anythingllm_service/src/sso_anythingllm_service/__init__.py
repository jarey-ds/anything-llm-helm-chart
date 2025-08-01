"""Service layer."""

# Import service implementations
from pathlib import Path

# Import interfaces
from sso_anythingllm_service.interfaces import SSOServiceInterface, UserServiceInterface
from sso_anythingllm_service.sso_service import SSOService
from sso_anythingllm_service.user_service import UserService

# Read version from VERSION file
version_file = Path(__file__).parents[2] / "VERSION"
if not version_file.exists():
    raise FileNotFoundError(f"VERSION file not found at {version_file}. Ensure the VERSION file exists in the package")
__version__ = version_file.read_text().strip()

__all__ = [
    "__version__",
    # Service implementations
    "SSOService",
    "UserService",
    # Service interfaces
    "UserServiceInterface",
    "SSOServiceInterface",
]
