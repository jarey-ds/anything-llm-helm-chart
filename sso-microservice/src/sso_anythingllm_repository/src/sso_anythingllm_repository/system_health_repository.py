from core_persistence_sqlalchemy.async_provider.raw_sql_repository import AsyncRawSQLRepository
from kink import inject


@inject(alias="DatabaseHealthRepository")
class SystemHealthRepository(AsyncRawSQLRepository):
    """Repository just used to invoke the PING method so DB status can be determined."""
