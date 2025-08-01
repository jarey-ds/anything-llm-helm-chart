from artemis_model_catalogue_service.monitoring.database_health_monitor import (
    ArtemisModelCatalogueDatabaseHealthMonitor,
)
from kink import di
from pyctuator.health.async_health_provider import AsyncHealthProvider


def setup_di():
    di[AsyncHealthProvider] = ArtemisModelCatalogueDatabaseHealthMonitor(
        name="primary-database", db_health_repository=di["DatabaseHealthRepository"]
    )

    print("Dependency injection finished.")
