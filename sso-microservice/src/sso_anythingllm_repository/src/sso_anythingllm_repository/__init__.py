"""Repository layer."""

from pathlib import Path

# Import interfaces
from sso_anythingllm_repository.interfaces import UserRepositoryInterface

# Import repository implementations
from sso_anythingllm_repository.user_repository import UserRepository

# setup_di()

# Read version from VERSION file
version_file = Path(__file__).parents[2] / "VERSION"
if not version_file.exists():
    raise FileNotFoundError(f"VERSION file not found at {version_file}. Ensure the VERSION file exists in the package")
__version__ = version_file.read_text().strip()


__all__ = [
    "__version__",
    # Repository implementations
    "UserRepository",
    # Repository interfaces
    "UserRepositoryInterface",
]
