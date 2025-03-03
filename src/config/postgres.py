from pydantic_settings import BaseSettings, SettingsConfigDict


class _PostgresSettings(BaseSettings):
    DATABASE_NAME: str
    DATABASE_HOSTNAME: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: str
    DATABASE_DEBUG_MODE: bool
    POOL_SIZE: int
    MAX_OVERFLOW: int
    model_config = SettingsConfigDict(extra='ignore', env_file='.env')
    

PostgresConfig = _PostgresSettings()
