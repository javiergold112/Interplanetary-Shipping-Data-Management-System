from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

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
