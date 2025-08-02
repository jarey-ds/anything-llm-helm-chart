import importlib.util

from kink import inject
from pyctuator.health.db_health_provider import DbHealthDetails, DbHealthStatus
from pyctuator.health.health_provider import HealthProvider, Status

from sso_anythingllm_repository.system_health_repository import SystemHealthRepository


@inject
class SSOAnythingLLMDatabaseHealthMonitor(HealthProvider):
    db_health_repository: SystemHealthRepository

    def __init__(
        self,
        db_health_repository: SystemHealthRepository,
        name: str = "db",
    ) -> None:
        self.name = name
        self.db_health_repository = db_health_repository

    def is_supported(self) -> bool:
        return importlib.util.find_spec("sqlalchemy") is not None

    def get_name(self) -> str:
        return self.name

    def get_health(self) -> DbHealthStatus:
        try:
            ping_result = self.db_health_repository._connector.ping()
            if ping_result["status"] == "connected":  # type: ignore[arg-type]
                return DbHealthStatus(status=Status.UP, details=DbHealthDetails("catalogue-database"))

            return DbHealthStatus(
                status=Status.UNKNOWN, details=DbHealthDetails("catalogue-database", "Pinging failed")
            )

        except Exception as e:  # pylint: disable=broad-except
            return DbHealthStatus(status=Status.DOWN, details=DbHealthDetails("catalogue-database", str(e)))
