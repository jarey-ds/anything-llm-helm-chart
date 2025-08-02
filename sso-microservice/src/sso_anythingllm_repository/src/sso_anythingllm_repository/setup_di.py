import os

from kink import di

from sso_anythingllm_repository import ApiKeyRepositoryInterface, UserRepositoryInterface
from sso_anythingllm_repository.api_key_repository import ApiKeyRepository
from sso_anythingllm_repository.config import AsyncPostgresConf
from sso_anythingllm_repository.user_repository import UserRepository


def setup_di():
    db_configuration: AsyncPostgresConf = AsyncPostgresConf(
        username=os.environ.get("POSTGRES_USER", "sso-anythingllm"),
        password=os.environ.get("POSTGRES_PASSWORD", "sso-anythingllm123"),
        database=os.environ.get("POSTGRES_DB", "sso_anythingllm"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
    )
    di[AsyncPostgresConf] = db_configuration
    di["async_engine"] = db_configuration.engine
    di["sync_engine"] = db_configuration.sync_engine
    di[UserRepositoryInterface] = UserRepository(db_config=db_configuration)
    di[ApiKeyRepositoryInterface] = ApiKeyRepository(db_config=db_configuration)
