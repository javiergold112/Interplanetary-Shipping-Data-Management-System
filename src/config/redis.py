from pydantic_settings import BaseSettings, SettingsConfigDict


class _RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    model_config = SettingsConfigDict(extra='ignore', env_file='.env')
    

RedisConfig = _RedisSettings()
