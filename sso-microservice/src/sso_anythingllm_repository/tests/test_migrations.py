import time
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from kink import di
from sqlalchemy import text
from testcontainers.postgres import PostgresContainer

from sso_anythingllm_repository.config import AsyncPostgresConf

MIGRATIONS_PATH = Path(__file__).parents[1] / "migrations"
ALEMBIC_INI_PATH = Path(__file__).parents[3] / "alembic.ini"


@pytest.fixture(scope="session")
def postgres_url():
    with PostgresContainer("postgres:15").with_bind_ports(5432) as postgres:
        time.sleep(2)
        # Create AsyncPostgresConf with container connection details
        dsn = postgres.get_connection_url(driver="asyncpg")
        print(f"Connection URL: {dsn}")

        postgres_conf = AsyncPostgresConf(
            host=postgres.get_container_host_ip(),
            port=int(postgres.get_exposed_port(5432)),
            username=postgres.username,
            password=postgres.password,
            database=postgres.dbname,
        )
        di[AsyncPostgresConf] = postgres_conf
        yield postgres.get_connection_url().replace("postgresql://", "postgresql+psycopg2://")


@pytest.fixture
def alembic_cfg(postgres_url):
    alembic_cfg = Config(str(ALEMBIC_INI_PATH))
    alembic_cfg.set_main_option("script_location", str(MIGRATIONS_PATH))
    return alembic_cfg


def test_migrations_up_and_down(alembic_cfg):
    # Upgrade to head
    command.upgrade(alembic_cfg, "head")

    # Check a table exists
    db_conf: AsyncPostgresConf = di[AsyncPostgresConf]
    engine = db_conf.sync_engine
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename='anythingllm_user';"))
        assert result.first() is not None

    # Downgrade to base
    command.downgrade(alembic_cfg, "base")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename='anythingllm_user';"))
        assert result.first() is None
