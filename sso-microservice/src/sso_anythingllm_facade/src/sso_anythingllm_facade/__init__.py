"""Facade layer."""

# Import facade implementations
from pathlib import Path

from sso_anythingllm_facade.interfaces.sso_facade_interface import SSOFacadeInterface
from sso_anythingllm_facade.sso_facade import SSOFacade

# Read version from VERSION file
version_file = Path(__file__).parents[2] / "VERSION"
if not version_file.exists():
    raise FileNotFoundError(f"VERSION file not found at {version_file}. Ensure the VERSION file exists in the package")
__version__ = version_file.read_text().strip()


__all__ = [
    "__version__",
    # Facade implementations
    "SSOFacade",
    # Facade interfaces
    "SSOFacadeInterface",
]
