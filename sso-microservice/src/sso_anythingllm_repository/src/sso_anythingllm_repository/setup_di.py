import os

from kink import di

from sso_anythingllm_repository.config import AsyncPostgresConf


def setup_di():
    db_configuration: AsyncPostgresConf = AsyncPostgresConf(
        username=os.environ.get("POSTGRES_USER", "sso_anythingllm"),
        password=os.environ.get("POSTGRES_PASSWORD", "sso_anythingllm123"),
        database=os.environ.get("POSTGRES_DB", "sso_anythingllm"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
    )
    di[AsyncPostgresConf] = db_configuration
