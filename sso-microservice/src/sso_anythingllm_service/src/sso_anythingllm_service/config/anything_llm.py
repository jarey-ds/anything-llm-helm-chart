from pydantic_settings import BaseSettings, SettingsConfigDict


class AnythingLLMConfig(BaseSettings):
    """Configuration class meant to host any config having to do with the AnythingLLM instance, specially relevant
    to host all the configuration needed to consume the AnythingLLM Rest API."""

    model_config = SettingsConfigDict(env_prefix="ANYTING_LLM_", enable_decoding=False)
    url: str
    admin_user: str
    admin_password: str
