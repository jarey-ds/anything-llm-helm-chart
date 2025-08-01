from pydantic import BaseModel
from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine, create_async_engine


class AsyncPostgresConf(BaseModel):
    username: str
    password: str
    host: str
    port: int
    database: str

    @property
    def engine(self) -> AsyncEngine:
        """SQLAlchemy engine"""
        return create_async_engine(url=self.url)

    @property
    def sync_engine(self) -> Engine:
        # Create a sync URL by replacing the async driver with sync driver
        sync_url = URL.create(
            drivername="postgresql+psycopg2",  # Use psycopg2 for sync operations
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        return create_engine(url=sync_url)

    @property
    def url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
