from pydantic_settings import BaseSettings, SettingsConfigDict


class _AppSettings(BaseSettings):
    FETCH_INTERVAL: int
    model_config = SettingsConfigDict(extra='ignore', env_file='.env')
    

AppConfig = _AppSettings()
